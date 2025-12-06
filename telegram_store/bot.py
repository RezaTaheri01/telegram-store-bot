# Telegram
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ContextTypes,
)

# Others
from decimal import Decimal
import logging
from logging.handlers import RotatingFileHandler
from asgiref.sync import sync_to_async
import asyncio
import aiohttp
from cachetools import TTLCache, LRUCache

from bot_settings import *

# Timezone
import timezonefinder
from datetime import datetime, timedelta
from pytz import timezone as pytz_timezone
from django.utils import timezone

# Django
import os
import django
from django.db import transaction
from django.db.models import Exists, OuterRef

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_store.settings')
django.setup()

if __name__ == "__main__":
    from products.models import Category, Product, ProductDetail
    from payment.models import Transaction, TonCursor
    from users.models import UserData, BotSettings


# region Logs
logger = logging.getLogger(__name__)
logger.setLevel(logging.WARN)

# Rotate log after it reaches 5 MB, keep 5 backup files
handler = RotatingFileHandler(
    "bot_logs.log", maxBytes=5*1024*1024, backupCount=5
)
formatter = logging.Formatter(
    '%(asctime)s - %(name)s - %(levelname)s - %(message)s'
)
handler.setFormatter(formatter)
logger.addHandler(handler)
# endregion


# region Global Variables
# TTLCache: maxsize 1 because you only have one settings object, TTL 10 minutes
ton_price: TTLCache = TTLCache(maxsize=1, ttl=3600)
settings_cache: TTLCache = TTLCache(maxsize=1, ttl=600)
language_cache: TTLCache = TTLCache(maxsize=1000, ttl=600)
timezone_cache: TTLCache = TTLCache(maxsize=1000, ttl=600)
seen_hashes_cache: LRUCache = LRUCache(maxsize=10000) # keep 10k most recent tx hashes

lang_keys = list(texts.keys())
# endregion


# region setting

def _get_settings_sync():
    # Check cache first
    if "settings" in settings_cache:
        return settings_cache["settings"]

    s = BotSettings.objects.first()
    if s is None:
        raise ValueError("BotSettings missing.")

    # Store in cache
    settings_cache["settings"] = s
    return s


async def get_settings():
    return await sync_to_async(_get_settings_sync)()


async def update_setting(update: Update, context: CallbackContext) -> None:
    # Clear cached settings manually
    settings_cache.clear()
    await update.message.delete()
    
# endregion


# region Menu Balance

# active command: /start and /menu
async def start_menu(update: Update, context: CallbackContext, query: CallbackQuery=None) -> None:
    user_id = update.effective_user.id
    usr_lng = await user_language(user_id=user_id)

    user = update.effective_user
    if user.username is None:
        username = f"{user.first_name or ''} {user.last_name or ''}".strip()
    else:
        username = f"@{user.username}"

    try:
        await check_create_account(update)  # Create a user if not exist
        await send_message(update=update,
                           query=query,
                           txt=texts[usr_lng]["textStart"].format(username),
                           reply_markup=buttons[usr_lng]["main_menu_markup"])
    except Exception as e:
        logger.error(f"Error in start_menu function: {e}")
        await send_message(update=update,
                            txt=texts[usr_lng]["textError"],
                            reply_markup=buttons[usr_lng]["main_menu_markup"])

# active command: /set_timezone
async def timezone_hint(update: Update, context: CallbackContext) -> None:
    user_id = update.effective_user.id
    usr_lng = await user_language(user_id)

    try:
        await check_create_account(update)  # Create a user if not exist
        await update.message.reply_text(
            text=texts[usr_lng]["textTimezone"],
        )
    except Exception as e:
        logger.error(f"Error in timezone_hint function: {e}")
        await send_message(update=update,
                           txt=texts[usr_lng]["textError"])


async def user_balance(update: Update, context: CallbackContext, query: CallbackQuery=None) -> None:
    user_id = update.effective_user.id
    usr_lng = await user_language(user_id)
    
    try:
        s: BotSettings = await get_settings()
        balance = await sync_to_async(
            lambda: UserData.objects.filter(id=user_id)
                                    .values_list("balance", flat=True)
                                    .first(),
            thread_sensitive=True
        )()

        if balance is None:
            await check_create_account(update)
            balance = 0

        await send_message(update=update,
                           query=query,
                           txt=texts[usr_lng]["textBalance"].format(balance, s.wallet_currency_sign),
                           reply_markup=buttons[usr_lng]["balance_markup"])
    except Exception as e:
        logger.error(f"Error in user_balance function: {e}")
        await send_message(update=update,
                            query=query,
                            txt=texts[usr_lng]["textError"],
                            reply_markup=buttons[usr_lng]["back_menu_markup"])

# endregion


# region TON

@sync_to_async
def get_last_lt() -> int:
    obj, _ = TonCursor.objects.get_or_create(key="deposit_cursor", defaults={"last_lt": 0})
    return obj.last_lt


@sync_to_async
def update_last_lt(new_lt):
    with transaction.atomic():
        cursor = TonCursor.objects.select_for_update().get(key="deposit_cursor")
        cursor.last_lt = new_lt
        cursor.save()

     
@sync_to_async
def record_failed_tx(tx_hash, amount, comment, price, price_currency, lt=None):
    try:
        Transaction.objects.update_or_create(
            tx_id=str(tx_hash),  # lookup field
            defaults={           # fields to update or create
                "lt": lt,
                "amount": Decimal(amount),
                "comment": str(comment),
                "price_per_ton": Decimal(price),
                "price_currency": str(price_currency),
                "atomic_failed": True
            }
        )
        return True
    except:
        return False

# Todo: add retry
async def get_ton_price():
    global ton_price
    s: BotSettings = await get_settings()
    currency = s.wallet_currency.lower()

    apis = [
        {     
            # 1 requests per second
            # https://toncenter.com/api/       
            "url": "https://tonapi.io/v2/rates",
            "params": {"tokens": "ton",
                       "currencies": currency,
                       "api_key": s.ton_api_io_key},
            "headers": None,
            "parse": lambda data: data["rates"]["TON"]["prices"][currency.upper()] 
        },
        {
            # free tier 10k/month
            "url": "https://api.coingecko.com/api/v3/simple/price",
            "params": {"ids": "the-open-network", "vs_currencies": currency},
            "headers": None,
            "parse": lambda data: data.get("the-open-network", {}).get(currency)
        },
        {
            # CMC (paid/free key)
            "url": "https://pro-api.coinmarketcap.com/v1/cryptocurrency/quotes/latest",
            "params": {"symbol": "TON", "convert": currency.upper()},
            "headers": {"X-CMC_PRO_API_KEY": s.cmc_api_key},
            "parse": lambda data: data["data"]["TON"]["quote"][currency.upper()]["price"]
        }
    ]

    for api in apis:
        try:
            async with aiohttp.ClientSession() as session:
                resp = await session.get(
                    api["url"],
                    params=api.get("params"),
                    headers=api.get("headers"),
                    timeout=5
                )
                
                if resp.status != 200:
                    logger.warning(f"HTTP {resp.status} from {api['url']}")
                    continue

                data = await resp.json()
                
                price = api["parse"](data)
                if price is not None:
                    ton_price.update(price=round(float(price), 3))
                    return ton_price

                logger.warning(f"Price not found in {api['url']} response")

        except Exception as e:
            logger.warning(f"Failed fetching price from {api['url']}: {e}")

    logger.error("All TON price APIs failed")
    return None


async def ton_price_job():
    s: BotSettings = await get_settings()
    while True:
        await get_ton_price()
        await asyncio.sleep(s.ton_price_delay)


""" 
Todo 
* Handle High traffic / large number of transactions
* Ensuring atomic updates (no double spend, no missed credits)
* Retrying failed transactions
"""
@sync_to_async
def apply_transaction(user_id, ton_amount, tx_hash, balance_update: Decimal, wallet_currency, comment, lt=None) -> bool:
    try:
        with transaction.atomic():
            price = ton_price.get("price")
            if price is None:
                return False
            
            user = UserData.objects.select_for_update().get(id=user_id)

            user.balance += balance_update
            user.save()
                                        
            Transaction.objects.create(
                user=user,
                amount=ton_amount,
                comment=comment,
                tx_id=tx_hash,
                lt=lt,
                price_per_ton=Decimal(price),
                price_currency=wallet_currency
            )

        return True
    except Exception as e:
        logger.error(f"Atomic rolled back in apply_transaction(): {e}")
        return False


# https://toncenter.com/api/
async def ton_polling(app):
    ton_api_url = "https://toncenter.com/api/v2/getTransactions"
    s: BotSettings = await get_settings()

    params = {
        "address": s.ton_deposit_address,
        "limit": s.ton_fetch_limit,
        "api_key": s.ton_network_api_key,
    }

    try:
        async with aiohttp.ClientSession() as session:
            async with session.get(ton_api_url, params=params) as resp:
                data = await resp.json()
    except Exception as e:
        logger.error(f"Failed to fetch TON transactions: {e}")
        return

    price = ton_price.get("price")
    if price is None:
        await get_ton_price()
        logger.warning("TON price not available, skipping transaction processing")
        return

    last_transaction_lt = await get_last_lt()
    
    # Extract & filter NEW transactions
    txs = data.get("result", [])
    new_txs = []
    for tx in txs:
        tx_id = tx.get("transaction_id", {})
        tx_lt = tx_id.get("lt")
        if tx_lt is None:
            continue
        if int(tx_lt) > last_transaction_lt:
            new_txs.append(tx)

    if not new_txs:
        return

    # Sort by lt ASC → oldest first
    new_txs.sort(key=lambda t: t["transaction_id"]["lt"])

    max_success_lt = last_transaction_lt

    # Process each transaction
    for tx in new_txs:
        tx_id = tx.get("transaction_id", {})
        tx_hash = tx_id.get("hash")
        tx_lt = tx_id.get("lt")

        try:
            if not tx_hash or tx_hash in seen_hashes_cache:
                continue
            seen_hashes_cache[tx_hash] = True

            msg = tx.get("in_msg", {})
            comment_hex = msg.get("message", "").strip()
            value = int(msg.get("value", 0))

            if not comment_hex:
                continue

            try:
                user_id = int(comment_hex, 16)
            except ValueError:
                logger.warning(f"Invalid comment (not hex): {comment_hex}")
                continue

            # Check if tx exists
            exists = await sync_to_async(
                lambda: Transaction.objects.filter(
                    comment=comment_hex, tx_id=tx_hash
                ).exists(),
                thread_sensitive=True,
            )()
            if exists:
                continue

            # Check user exists
            user_exist = await sync_to_async(
                lambda: UserData.objects.filter(id=user_id).exists(),
                thread_sensitive=True,
            )()
            if not user_exist:
                logger.warning(f"User not found for id {user_id}")
                continue

            # Calculate TON deposit
            ton_amount = value / 1e9
            balance_update = Decimal(ton_amount) * Decimal(price)

            # Apply transaction atomically
            s: BotSettings = await get_settings()
            success = await apply_transaction(
                user_id, ton_amount, tx_hash, balance_update, s.wallet_currency, comment_hex, tx_lt
            )

            if not success:
                logger.warning(f"Failed atomic apply_transaction for lt {tx_lt}")
                res = await record_failed_tx(tx_hash=tx_hash,
                                             amount=ton_amount,
                                             comment=comment_hex,
                                             price=price,
                                             price_currency=s.wallet_currency,
                                             lt=tx_lt,
                                            )
                if not res and tx_hash in seen_hashes_cache:
                    del seen_hashes_cache[tx_hash] 
                else:   
                    # Mark LT as successfully processed
                    max_success_lt = int(tx_lt)
                continue

            # Mark LT as successfully processed
            max_success_lt = int(tx_lt)

            # Notify user
            try:
                usr_lng = await user_language(user_id)
                text = texts[usr_lng]["textChargeAccount"].format(
                    ton_amount, price, s.wallet_currency
                )
                await send_message_with_retry(
                    bot=app.bot, chat_id=user_id, text=text,
                    retry=2, parse_mode="Markdown"
                )
            except Exception as e:
                logger.warning(f"Failed to notify user {user_id}: {e}")

        except Exception as e:
            if tx_hash and tx_hash in seen_hashes_cache:
                del seen_hashes_cache[tx_hash]
            logger.error(f"Error processing transaction {tx}: {e}")
            break  # STOP. Do not skip ahead.

    # Update last_transaction_lt ONLY AFTER all successful operations
    if max_success_lt > last_transaction_lt:
        await update_last_lt(max_success_lt)


async def ton_polling_job(app):
    s: BotSettings = await get_settings()
    while True:
        await ton_polling(app)
        await asyncio.sleep(s.ton_network_delay)


# Failed Transactions
@sync_to_async
def fetch_failed_transactions():
    """Fetch unresolved failed TON transactions."""
    return list(Transaction.objects.filter(atomic_failed=True, is_delete=False))


@sync_to_async
def apply_failed_transaction(user_id, tx_hash, balance_update: Decimal) -> bool:
    try:
        with transaction.atomic():
            price = ton_price.get("price")
            if price is None:
                return False
            
            user = UserData.objects.select_for_update().get(id=user_id)

            user.balance += balance_update
            user.save()
                            
            Transaction.objects.filter(tx_id=tx_hash).update(
                user=user,
                atomic_failed=False
            )

        return True
    except Exception as e:
        logger.error(f"Atomic rolled back in apply_transaction(): {e}")
        return False


async def ton_failed_transactions(app):
    """Retry unresolved failed transactions."""
    failed_txs = await fetch_failed_transactions()
    if not failed_txs:
        return

    # s: BotSettings = await get_settings()
    price = ton_price.get("price")
    if price is None:
        logger.warning("TON price not available, skipping failed transaction processing")
        return  # Skip if TON price unavailable

    for tx in failed_txs:
        try:
            user_id = int(tx.comment, 16)
            # Attempt to apply the transaction atomically
            success = await apply_failed_transaction(
                user_id=user_id,
                tx_hash=tx.tx_id,
                balance_update=Decimal(tx.amount) * Decimal(price),
            )
            if success:
                # Notify user
                try:
                    usr_lng = await user_language(user_id)
                    text = texts[usr_lng]["textChargeAccount"].format(
                        tx.amount, price, tx.price_currency
                    )
                    await send_message_with_retry(
                        bot=app.bot, chat_id=user_id,
                        text=text, retry=2, parse_mode="Markdown"
                    )
                except Exception as e:
                    logger.warning(f"Failed to notify user {tx.comment}: {e}")

        except Exception as e:
            logger.error(f"Failed to process failed transaction {tx.tx_id}: {e}")


async def failed_transactions_job(app):
    """Background loop to retry failed transactions periodically."""
    s: BotSettings = await get_settings()
    while True:
        await ton_failed_transactions(app)
        await asyncio.sleep(s.failed_transactions_delay)

# endregion


# region Pay Link

async def generate_ton_link(user_id: int, deposit_address: str) -> str:
    """Return a ton:// link with the user's hex ID as comment."""
    return f"ton://transfer/{deposit_address}?text={hex(user_id).lower()}"


async def pay_link(update: Update, context: ContextTypes.DEFAULT_TYPE, query: CallbackContext=None):
    user_id = update.effective_user.id
    usr_lng = await user_language(user_id)
    
    s: BotSettings = await get_settings()

    price = ton_price.get("price")
    if price is None:
        await send_message(update=update,
                            query=query,
                            txt=texts[usr_lng]["textErrorNoPrice"],
                            reply_markup=buttons[usr_lng]["balance_markup"])
        return
    
    await check_create_account(update)
    
    link = await generate_ton_link(user_id, s.ton_deposit_address)

    text = (
        texts[usr_lng]["textPaymentLink"].format(
            s.ton_deposit_address, hex(user_id).lower(), price, s.wallet_currency_sign)
    )

    pay_key = [
        [InlineKeyboardButton(text=texts[usr_lng]["textPayButton"], url=link)],
        [InlineKeyboardButton(
            text=texts[usr_lng]["telegramWallet"], url=s.telegram_wallet_link)],
        [InlineKeyboardButton(texts[usr_lng]["buttonBackMainMenu"], callback_data=main_menu_cb)]
    ]

    pay_key_markup = InlineKeyboardMarkup(pay_key)

    try:
        await send_message(update=update,
                           query=query,
                           txt = text,
                           reply_markup=pay_key_markup,
                           parse_mode="Markdown"
        )
    except Exception as e:
        logger.error(f"Error in pay_link function: {e}")
        await send_message(update=update,
                            query=query,
                            txt=texts[usr_lng]["textErrorNoPrice"],
                            reply_markup=buttons[usr_lng]["balance_markup"])

# endregion


# region Manage account

async def account_menu_call_back(query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)
    full_name = f"{query.from_user.first_name or ''} {query.from_user.last_name or ''}".strip()
    try:
        await send_message(query=query,
                    txt=texts[usr_lng]["textAccountMenu"].format(full_name),
                    reply_markup=buttons[usr_lng]["account_keys_markup"])   
    except Exception as e:
        logger.error(f"Error in account_menu_call_back function: {e}")
        await send_message(query=query,
                           txt=texts[usr_lng]["textError"],
                           reply_markup=buttons[usr_lng]["back_menu_markup"])


async def account_info(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    usr_lng = await user_language(user_id)
    s: BotSettings = await get_settings()

    try:
        user_data = await sync_to_async(UserData.objects.filter(id=user_id).first, thread_sensitive=True)()
        if user_data is None:
            await send_message(query=query,
                            txt=texts[usr_lng]["textNotUser"],
                            reply_markup=buttons[usr_lng]["back_to_acc_markup"])
            return

        text = texts[usr_lng]["textAccInfo"].format(
            user_data.username,
            (user_data.first_name or "") + " " + (user_data.last_name or ""),
            user_data.balance,
            s.wallet_currency_sign)
        
        await send_message(query=query,
                        txt= text,
                        reply_markup=buttons[usr_lng]["back_to_acc_markup"])
    except Exception as e:
        logger.error(f"Error in account_info function: {e}")


@sync_to_async
def get_transactions(user_id, start, limit):
    qs = Transaction.objects.filter(user_id=user_id, is_delete=False, atomic_failed=False)
    total = qs.count()
    transactions = list(qs.order_by('-paid_time')[start:start+limit])
    return transactions, total

# Todo: Move it to website
async def account_transactions(query: CallbackQuery) -> None:
    def format_utc_offset(offset: float):
        hours = int(offset)  # whole hours
        minutes = int(abs(offset - hours) * 60)

        formatted = f"{hours:+03d}:{minutes:02d}"

        return formatted

    user_id = query.from_user.id
    usr_lng = await user_language(user_id)
    usr_utc_offset = await user_timezone(user_id)

    formatted_utc_offset = format_utc_offset(usr_utc_offset)

    try:
        temp: list = query.data.split('_')
        if len(temp) == 1:
            start_index = 0
        else:
            # Extract start index from callback data
            start_index: int = int(query.data.split('_')[1])
            if start_index < 0:
                return

    except (IndexError, ValueError):
        await query.answer(texts[usr_lng]["textNotFound"], show_alert=True)
        return

    try:
        s: BotSettings = await get_settings()
        # Fetch transactions and total count
        user_transactions, total_transactions = await get_transactions(user_id, start_index, s.number_of_transactions)

        if user_transactions is None:
            if start_index == 0:
                await send_message(query=query,
                                   txt=texts[usr_lng]["textNoTransaction"],
                                   reply_markup=buttons[usr_lng]["back_to_acc_markup"])
            return

        # Calculate page info
        current_page = start_index // s.number_of_transactions + 1
        total_pages = (total_transactions +
                       s.number_of_transactions - 1) // s.number_of_transactions

        # Page number
        result_data = texts[usr_lng]["textTransaction"].format(
            f'{current_page}/{total_pages}')
        result_data += "\n\n"

        # Build transaction list
        for t in user_transactions:
            new_time = t.paid_time + timedelta(hours=usr_utc_offset)
            formatted_time = new_time.strftime("%Y-%m-%d %H:%M:%S")
            amount = round(t.amount, 6)  # round for cleaner display
            price = t.price_per_ton
            currency = t.price_currency

            result_data += texts[usr_lng]["textTransactionDetail"].format(price,
                                                                          currency,
                                                                          t.tx_id,
                                                                          amount,
                                                                          formatted_time,
                                                                          formatted_utc_offset) + SEP_LINE

        # Pagination buttons
        transactions_keys = []

        # Add "Previous" button only if there is a previous page
        if start_index > 0:
            transactions_keys.append(
                InlineKeyboardButton(
                    texts[usr_lng]["textPrev"],
                    callback_data=f"{transactions_cb}_{start_index - s.number_of_transactions}"
                )
            )

        # Add "Next" button only if there is a next page
        if start_index + s.number_of_transactions < total_transactions:
            transactions_keys.append(
                InlineKeyboardButton(
                    texts[usr_lng]["textNext"],
                    callback_data=f"{transactions_cb}_{start_index + s.number_of_transactions}"
                )
            )

        # Add buttons for account and main menu navigation
        navigation_buttons = [
            [InlineKeyboardButton(
                texts[usr_lng]["buttonAccount"], callback_data=account_menu_cb)],
            [InlineKeyboardButton(
                texts[usr_lng]["buttonBackMainMenu"], callback_data=main_menu_cb)]
        ]

        # Combine all buttons
        if transactions_keys:
            transactions_markup = InlineKeyboardMarkup(
                [transactions_keys] + navigation_buttons)
        else:
            transactions_markup = InlineKeyboardMarkup(navigation_buttons)

        await send_message(query=query,
                    txt=result_data,
                    reply_markup=transactions_markup,
                    parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in account_transactions function: {e}")


@sync_to_async
def get_user_purchases(user_id, start_index, limit):
    qs = ProductDetail.objects.filter(
        is_purchased=True,
        buyer__id=user_id,
        is_delete=False
    ).select_related('product').order_by('-purchase_date')

    total = qs.count()  # total number of purchases
    purchases = list(qs[start_index:start_index + limit])  # paginated slice
    return purchases, total

# Todo: Move it to website
async def user_purchase_products(query: CallbackQuery) -> None:
    def format_utc_offset(offset: float):
        hours = int(offset)  # whole hours
        minutes = int(abs(offset - hours) * 60)

        formatted = f"{hours:+03d}:{minutes:02d}"

        return formatted

    user_id = query.from_user.id
    usr_lng = await user_language(user_id)
    usr_utc_offset = await user_timezone(user_id)

    formatted_utc_offset = format_utc_offset(usr_utc_offset)
    
    try:
        temp: list = query.data.split('_')
        if len(temp) == 1:
            start_index = 0
        else:
            # Extract start index from callback data
            start_index: int = int(query.data.split('_')[1])
            if start_index < 0:
                return

    except (IndexError, ValueError):
        await query.answer(texts[usr_lng]["textNotFound"], show_alert=True)
        return

    try:
        s: BotSettings = await get_settings()
        # Fetch products and total count
        user_products, total_purchase = await get_user_purchases(
            user_id, start_index, s.number_of_product
        )

        if not user_products:
            if start_index == 0:
                await send_message(query=query,
                    txt=texts[usr_lng]["textNotFound"],
                    reply_markup=buttons[usr_lng]["back_to_acc_markup"])
            return

        # Calculate page info
        current_page = start_index // s.number_of_product + 1
        total_pages = (total_purchase + s.number_of_product -
                       1) // s.number_of_product

        # Page number
        result_data = texts[usr_lng]["textProducts"].format(
            f'{current_page}/{total_pages}')
        result_data += "\n\n"
        for p in user_products:
            product_name = await get_name(usr_lng, p.product)
            # Add usr_utc_offset hours
            new_time = p.purchase_date + timedelta(hours=usr_utc_offset)
            # Format paid_time using strftime
            formatted_time = new_time.strftime("%Y-%m-%d %H:%M:%S")
            result_data += texts[usr_lng]["textProductDetailList"].format(
                product_name,
                formatted_time,
                formatted_utc_offset,
                p.details,
            ) + SEP_LINE

        # Pagination buttons
        products_keys = []

        # Add "Previous" button only if there is a previous page
        if start_index > 0:
            products_keys.append(
                InlineKeyboardButton(
                    texts[usr_lng]["textPrev"],
                    callback_data=f"{purchase_products_cb}_{start_index - s.number_of_product}"
                )
            )

        # Add "Next" button only if there is a next page
        if start_index + s.number_of_product < total_purchase:
            products_keys.append(
                InlineKeyboardButton(
                    texts[usr_lng]["textNext"],
                    callback_data=f"{purchase_products_cb}_{start_index + s.number_of_product}"
                )
            )

        # Add buttons for account and main menu navigation
        navigation_buttons = [
            [InlineKeyboardButton(
                texts[usr_lng]["buttonAccount"], callback_data=account_menu_cb)],
            [InlineKeyboardButton(
                texts[usr_lng]["buttonBackMainMenu"], callback_data=main_menu_cb)]
        ]

        # Combine all buttons
        if products_keys:
            products_markup = InlineKeyboardMarkup(
                [products_keys] + navigation_buttons)
        else:
            products_markup = InlineKeyboardMarkup(navigation_buttons)

        await send_message(query=query,
                           txt=result_data,
                           reply_markup=products_markup,
                           parse_mode="Markdown")

    except Exception as e:
        logger.error(f"Error in user_purchase_products function: {e}")


# Create a user account if it doesn't exist
async def check_create_account(update: Update) -> None:
    user_id = update.effective_user.id
    usr_lng = await user_language(user_id)
    found: bool = await sync_to_async(UserData.objects.filter(id=user_id).exists, thread_sensitive=True)()

    if not found:
        try:
            first_name = update.effective_user.first_name or None
            last_name = update.effective_user.last_name or None
            username = update.effective_user.username or None

            new_user = UserData(
                id=user_id,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )
            await sync_to_async(new_user.save, thread_sensitive=True)()
        except Exception as e:
            await send_message(update=update,
                               txt=texts[usr_lng]["textError"])
            logger.error(f"Error in check_create_account function: {e}")


async def change_user_language(query: CallbackQuery):
    user = await sync_to_async(UserData.objects.filter(id=query.from_user.id).first, thread_sensitive=True)()

    try:
        next_lang_idx = (lang_keys.index(user.language) + 1) % len(lang_keys)
        user.language = lang_keys[next_lang_idx]
    except:
        logger.error("Can't find next language in change_user_language function.")
        user.language = LANG1

    await sync_to_async(user.save, thread_sensitive=True)()
    language_cache[user.id] = user.language

    await send_message(query=query,
                       txt=texts[user.language]["textMenu"],
                       reply_markup=buttons[user.language]['main_menu_markup'])


async def get_user_location(update: Update, context: ContextTypes.DEFAULT_TYPE):
    usr_id = update.effective_user.id
    usr_lng = await user_language(usr_id)
    user_location = update.message.location
    tf = timezonefinder.TimezoneFinder()
    timezone_str = tf.timezone_at(
        lng=user_location.longitude, lat=user_location.latitude)

    if timezone_str:
        user_time_zone = pytz_timezone(timezone_str)
        # now_in_user_timezone = datetime.now(user_timezone)

        # Calculate timezone difference in hours (as a float) using .utcoffset()
        timezone_offset = user_time_zone.utcoffset(
            datetime.now()).total_seconds() / 3600

        await send_message(update=update,
                           txt=f"{texts[usr_lng]['textTimezoneSuccess']}\n{timezone_str}")
        # await send_message(update=update,
        #                    txt=f"Your timezone is: {timezone_str} {now_in_user_timezone}")
        # await send_message(update=update,
        #                    txt=f"UTC Offset: {timezone_offset:.2f} hours")

        # Update user timezone and offset
        user = await sync_to_async(UserData.objects.filter(id=usr_id).first, thread_sensitive=True)()
        # Assuming `utc_offset` is a FloatField in your model
        user.utc_offset = timezone_offset
        await sync_to_async(user.save, thread_sensitive=True)()
        timezone_cache[usr_id] = timezone_offset

    else:
        await send_message(update=update,
                           txt=texts[usr_lng]["textTimezoneFailed"])

# endregion


# region Products

async def get_name(user_lang: str, current_object) -> str:
    try:
        current_name = eval(f"current_object.name_{user_lang}")
        if not current_name:
            logger.error(
                f"name {current_object.name} for language {user_lang} not founded return {current_object.name}")
            return current_object.name
        return current_name
    except:  # return main name field
        logger.error("error in get_name function: language not founded return name base on LANG1")
        return current_object.name or None


async def get_description(user_lang: str, current_object: Product) -> str:
    try:
        current_description = eval(f"current_object.description_{user_lang}")
        if not current_description:
            return current_object.description
        return current_description
    except:  # return main name field
        logger.error("error in get_description function: language not founded return name base on LANG1")
        return current_object.description or None


async def product_categories(query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)

  # Only categories that have at least one product with available ProductDetail
    categories_qs = Category.objects.annotate(
        has_available_products=Exists(
            ProductDetail.objects.filter(
                product__category=OuterRef('pk'),
                is_purchased=False,
                is_delete=False,
                product__is_delete=False
            )
        )
    ).filter(has_available_products=True)

    categories = await sync_to_async(list, thread_sensitive=True)(categories_qs)

    if not categories:
        await send_message(query=query,
                    txt=texts[usr_lng]["textNotFound"],
                        reply_markup=buttons[usr_lng]["back_menu_markup"])
        return
    try:
        s: BotSettings = await get_settings()
        # Create buttons for categories
        temp_keys = []
        for i in range(0, len(categories), s.category_in_row):
            row = await asyncio.gather(
                *[get_name(usr_lng, cat) for cat in categories[i:i + s.category_in_row]]
            )
            temp_keys.append(
                [InlineKeyboardButton(name, callback_data=f"{select_category_cb}_{cat.id}") for name, cat in
                 zip(row, categories[i:i + s.category_in_row])]
            )

        temp_keys.append(
            [InlineKeyboardButton(texts[usr_lng]["buttonBackMainMenu"], callback_data=main_menu_cb)])  # Add back button
        temp_reply_markup = InlineKeyboardMarkup(temp_keys)

        await send_message(query=query,
                    txt=texts[usr_lng]["textProductCategories"],
                    reply_markup=temp_reply_markup)
    except Exception as e:
        logger.error(f"Error in product_categories function: {e}")

@sync_to_async
def get_available_products(category_id):
    return list(
        Product.objects.annotate(
            has_available=Exists(
                ProductDetail.objects.filter(
                    product=OuterRef("pk"),
                    is_purchased=False,
                    is_delete=False
                )
            )
        ).filter(has_available=True, category_id=category_id, is_delete=False).order_by("order")
    )


async def products(update: Update, query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)
    # Detect if current message is an image
    is_photo = bool(query.message.photo)
    try:
        # Extract category ID from callback data
        cat_id: int = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(texts[usr_lng]["textInvalidCategory"], show_alert=True)
        return

    # Fetch available products asynchronously
    all_products = await get_available_products(category_id=cat_id)

    if not all_products:
        if not is_photo:
            await send_message(query=query,
                               txt=texts[usr_lng]["textNoProductFound"],
                               reply_markup=buttons[usr_lng]["back_to_cats_markup"])
        else:
            await send_message(update=update,
                               txt=texts[usr_lng]["textNoProductFound"],
                               reply_markup=buttons[usr_lng]["back_to_cats_markup"])
        return

    try:
        s: BotSettings = await get_settings()
        # Create buttons for products
        temp_keys = []
        for i in range(0, len(all_products), s.product_in_row):
            # Gather the product names asynchronously
            names = await asyncio.gather(
                *[get_name(usr_lng, prod) for prod in all_products[i:i + s.product_in_row]]
            )
            # Create a row of InlineKeyboardButtons
            row = [
                InlineKeyboardButton(
                    name, callback_data=f"{select_product_cb}_{prod.id}")
                for name, prod in zip(names, all_products[i:i + s.product_in_row])
            ]
            temp_keys.append(row)

        temp_keys.append(
            [InlineKeyboardButton(texts[usr_lng]["buttonBackMainMenu"], callback_data=main_menu_cb)])  # Add back button
        temp_keys.append([InlineKeyboardButton(
            texts[usr_lng]["textBackButton"], callback_data=categories_cb)])
        temp_reply_markup = InlineKeyboardMarkup(temp_keys)

        # Get category name
        current_cat: Category = await sync_to_async(Category.objects.filter(id=cat_id, is_delete=False).first,
                                                    thread_sensitive=True)()
        cat_name = ""
        if current_cat:
            cat_name = await get_name(usr_lng, current_cat) + " "
        if not is_photo:
            await send_message(query=query,
                    txt=texts[usr_lng]["textProductList"].format(cat_name),
                    reply_markup=temp_reply_markup)
        else:
            await send_message(update=update,
                               txt=texts[usr_lng]["textProductList"].format(cat_name),
                                reply_markup=temp_reply_markup)
    except Exception as e:
        logger.error(f"Error in products function: {e}")


async def product_payment_detail(query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)

    # Extract product ID from callback data
    try:
        prod_id: int = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(texts[usr_lng]["textInvalidProduct"], show_alert=True)
        return

    # Fetch product asynchronously
    product_detail = await sync_to_async(
        ProductDetail.objects.filter(
            product_id=prod_id, is_purchased=False
        ).select_related('product__category').first,
        thread_sensitive=True
    )()

    if not product_detail:
        await query.answer(texts[usr_lng]["textProductSoldOut"], show_alert=True)
        return

    try:
        # Count available items
        available_count = await sync_to_async(
            ProductDetail.objects.filter(product_id=prod_id, is_purchased=False).count,
            thread_sensitive=True
        )()

        # Get bot settings
        s: BotSettings = await get_settings()

        # Create inline keyboard
        temp_keys = [
            [InlineKeyboardButton(
                texts[usr_lng]["textPayButton"],
                callback_data=f'{payment_cb}_{product_detail.product.price}_{product_detail.product.id}'
            )],
            [InlineKeyboardButton(
                texts[usr_lng]["textBackButton"],
                callback_data=f'{select_category_cb}_{product_detail.product.category.id}'
            )],
        ]
        temp_reply_markup = InlineKeyboardMarkup(temp_keys)

        # Build product description
        description = await get_description(usr_lng, product_detail.product) or ""
        if description:
            description = SEP_LINE_HTML + description

        # Build message text
        product_price = product_detail.product.price
        ton_needed = round((product_price / ton_price['price']) + 0.05, 2)
        message_text = texts[usr_lng]["textPurchaseBill"].format(
            await get_name(usr_lng, product_detail.product),
            product_detail.product.price,
            f"{s.wallet_currency} (~{ton_needed} TON)",
            available_count
        ) + description

        # Decide whether to send image or text
        product_image = product_detail.product.image
        if not product_image or s.disable_product_images:
            # Text-only message
            await send_message(query=query,
                               txt=message_text,
                               reply_markup=temp_reply_markup)
        else:
            full_url = ""
            # Send photo with caption
            try:
                full_url = product_image.url
                if SITE_DOMAIN is not None:
                    full_url = f"{SITE_DOMAIN}{full_url}"
                    
                await query.message.reply_photo(
                    photo=full_url,
                    caption=message_text,
                    reply_markup=temp_reply_markup
                )
            except Exception as e:
                # Fallback to text if image fails
                # Text-only message
                await send_message(query=query,
                                txt=message_text,
                                reply_markup=temp_reply_markup)
                logger.error(f"Error sending product image {full_url}: {e}")

    except Exception as e:
        await query.answer(texts[usr_lng]["textNotFound"], show_alert=True)
        logger.error(f"Error in product_payment_detail function: {e}")


async def update_product_detail(query: CallbackQuery, prod_id: int, usr_lng: str):
    try:
        # Detect if current message is an image
        is_photo = bool(query.message.photo)
        
        available_count = await sync_to_async(
            ProductDetail.objects.filter(
                product_id=prod_id, is_purchased=False).count
        )()

        # Get the existing message text
        if not is_photo:
            text = query.message.text or ""
        else:
            text = query.message.caption or ""
            
        lines = text.split("\n")

        lines[2] = texts[usr_lng]["textPurchaseUpdateAvailable"].format(
            available_count)

        new_text = "\n".join(lines)

        if not is_photo:
            # Edit the message with updated count
            await send_message(query=query,
                               txt=new_text,
                                reply_markup=query.message.reply_markup  # reuse existing keyboard
                                )
        else:
            # Update the caption under the existing image
            await query.edit_message_caption(
                caption=new_text,
                reply_markup=query.message.reply_markup
            )
    except Exception as e:
        logger.error(f"Error updating product detail message: {e}")


async def payment(update: Update, context: CallbackContext, query: CallbackQuery):
    user_id = query.from_user.id
    usr_lng = await user_language(user_id)

    try:
        payment_amount: int = int(query.data.split('_')[1])
        prod_id: int = int(query.data.split('_')[2])
    except (IndexError, ValueError):
        await query.answer(texts[usr_lng]["textInvalidPaymentAmount"], show_alert=True)
        return

    # Run the atomic block in sync code via sync_to_async
    @sync_to_async
    def process_payment():
        with transaction.atomic():
            # Lock user row
            user = UserData.objects.select_for_update().filter(id=user_id).first()
            if not user:
                return "no_user", None, None

            if user.balance < payment_amount:
                return "not_enough", None, None

            # Lock product row and fetch related Product
            product_detail = ProductDetail.objects.select_for_update().select_related('product').filter(
                product_id=prod_id, is_purchased=False
            ).first()
            if not product_detail:
                return "sold_out", None, None

            # Update balances and product
            user.balance -= payment_amount
            product_detail.is_purchased = True
            product_detail.buyer = user
            product_detail.purchase_date = timezone.now()
            
            product_detail.save()
            user.save()
            
            # Return the related product name
            return "success", product_detail.details, product_detail.product
    
    try:
        status, product_details, product = await process_payment()
    except:
        status = "failed"
    
    if status == "failed":
        await query.answer(text=texts[usr_lng]["textPaymentFailed"], show_alert=True)
    elif status == "no_user":
        await query.answer(text=texts[usr_lng]["textNotUser"], show_alert=True)
    elif status == "not_enough":
        await query.answer(text=texts[usr_lng]["textNotEnoughMoney"], show_alert=True)
    elif status == "sold_out":
        await query.answer(text=texts[usr_lng]["textProductSoldOut"], show_alert=True)
    elif status == "success":
        await send_message_with_retry(
            bot=context.bot,
            chat_id=query.message.chat.id,
            text=texts[usr_lng]["textProductDetail"].format(f"`{product_details}`\n\n🛒 `{await get_name(usr_lng, product)}`"),
            parse_mode="Markdown"
        )
        await update_product_detail(query, prod_id, usr_lng)

# endregion


# region Handlers

async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query: CallbackQuery = update.callback_query
    query_data = query.data

    if query_data == main_menu_cb:  # Main Menu
        await start_menu(update, context, query)
    elif query_data == balance_cb:  # User Balance
        await user_balance(update, context, query)
    elif query_data == account_menu_cb:  # Account Menu
        await account_menu_call_back(query)
    elif query_data == account_info_cb:  # User Account Info
        await account_info(query)
    elif query_data == deposit_cb:  # Deposit Link
        await pay_link(update, context, query)
    elif query_data == categories_cb:  # Product Categories
        await product_categories(query)
    elif query_data == change_lang_cb:  # Product Categories
        await change_user_language(query)
    elif query_data.startswith(transactions_cb):  # User Transaction
        await account_transactions(query)
    elif query_data.startswith(purchase_products_cb):  # User Purchase Products
        await user_purchase_products(query)
    elif query_data.startswith(f"{select_category_cb}_"):  # Selected category
        await products(update, query)
    elif query_data.startswith(f"{select_product_cb}_"):  # Selected product
        await product_payment_detail(query)
    elif query_data.startswith(f"{payment_cb}_"):  # Payment processing
        await payment(update, context, query)

    await query.answer()  # Stop button animation
    return


# Global Error Handler
async def error_handler(update: Update, context: CallbackContext):
    try:
        logger.error(msg="Exception while handling an update:",
                     exc_info=context.error)
        # # Notify the user (optional)
        # if update and update.effective_user:
        #     await update.effective_message.reply_text('An error occurred. The bot will continue to work.')
    except Exception as e:
        logger.error(f"Error in error_handler: {e}")

# endregion


async def user_language(user_id: int):
    try:
        if user_id in language_cache:
            return language_cache[user_id]

        user = await sync_to_async(UserData.objects.filter(id=user_id).first, thread_sensitive=True)()
        if not user:
            language_cache[user_id] = LANG1
            return LANG1

        if user.language not in texts:
            user.language = LANG1
            await sync_to_async(user.save, thread_sensitive=True)()

        language_cache[user_id] = user.language
        return user.language

    except:
        return LANG1


async def user_timezone(user_id: int):
    try:
        if user_id not in timezone_cache:
            user = await sync_to_async(UserData.objects.filter(id=user_id).first, thread_sensitive=True)()
            if not user:
                timezone_cache[user_id] = 0
                return 0
            timezone_cache[user_id] = user.utc_offset

        return timezone_cache[user_id]
    except:
        return 0


async def send_message_with_retry(bot, chat_id, text: str, retry: int = 3, parse_mode=None):
    for attempt in range(retry):
        try:
            await bot.send_message(chat_id=chat_id, text=text, parse_mode=parse_mode)
            return True
        except Exception as e:
            if attempt < retry - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(
                    f"Failed to send message after {retry} attempts: {e}")
                return False
    return False


async def send_message(update: Update = None,
                       query: CallbackQuery = None,
                       txt: str = "Error",
                       reply_markup: InlineKeyboardMarkup=None,
                       parse_mode:str=None):
    try:
        if query is not None:
            await query.edit_message_text(txt, reply_markup=reply_markup, parse_mode=parse_mode)
        elif update is not None:
            await update.effective_chat.send_message(txt, reply_markup=reply_markup, parse_mode=parse_mode)
    except Exception as e:
        logger.error(f"Error in send_message function: {e}")
    

# Todo: Move them to Django(celery)
async def start_background_tasks(application):
    print("Bot start successfully")
    # background task for getting TON price
    asyncio.create_task(ton_price_job())
    asyncio.create_task(ton_polling_job(application))
    asyncio.create_task(failed_transactions_job(application))
    

# Main function
def main() -> None:
    app = Application.builder().token(TOKEN).post_init(start_background_tasks).build()

    handlers = [
        # Check account or create only here
        CommandHandler(UPDATE_SETTING_COMMAND, update_setting),
        CommandHandler("start", start_menu),
        CommandHandler("menu", start_menu),
        CommandHandler("balance", user_balance),
        CommandHandler("pay", pay_link),
        # CommandHandler("set_timezone", timezone_hint),
        # MessageHandler(filters.LOCATION, get_user_location),
        CallbackQueryHandler(callback_query_handler),
    ]

    app.add_handlers(handlers)
    app.add_error_handler(error_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
