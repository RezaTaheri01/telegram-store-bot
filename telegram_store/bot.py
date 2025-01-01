# import sys
import asyncio

# region bot settings
if __name__ == "__main__":
    from bot_settings import *
else:
    from bot_settings import texts, lang1
# endregion


# region Django Imports
import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_store.settings')
django.setup()

from users.models import UserData
from payment.models import Transactions

if __name__ == "__main__":
    from products.models import Category, Product, ProductDetail
# endregion


# region Telegram Imports
from telegram import Update, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
    ContextTypes,
)
from telegram import Bot
from asgiref.sync import sync_to_async
from decouple import config
# endregion


# region Logs
import logging

# Log errors
logger = logging.getLogger(__name__)

# Set up logging
logging.basicConfig(
    filename='logs.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN
)

# endregion


# region Global Variables

# Define states
ENTER_AMOUNT = 1

token = config("TOKEN")

bot_username = ""

# Todo: implement aging for better memory usage
language_cache: dict = {}


# endregion


# region Menu

async def start_menu(update: Update, context: CallbackContext) -> None:  # active command is /start
    usr_lng = await user_language(update.effective_user.id)
    full_name = f"{update.effective_user.first_name or ''} {update.effective_user.last_name or ''}".strip()
    try:
        await check_create_account(update)  # Create a user if not exist
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=texts[usr_lng]["textStart"].format(full_name),
            reply_markup=buttons[usr_lng]["main_menu_markup"],
        )
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(texts[usr_lng]["textError"], reply_markup=buttons[usr_lng]["main_menu_markup"])
        logger.error(f"Error in start_menu function: {e}")


async def menu_from_callback(query: CallbackQuery) -> None:
    usr_lng = await user_language(query.from_user.id)
    try:
        await query.edit_message_text(
            text=texts[usr_lng]["textMenu"],
            reply_markup=buttons[usr_lng]["main_menu_markup"],
        )
    except Exception as e:
        await query.edit_message_text(texts[usr_lng]["textError"],
                                      reply_markup=buttons[usr_lng]["main_menu_markup"])
        logger.error(f"Error in menu_from_callback function: {e}")


# endregion


# region Balance

async def user_balance(update: Update, context: CallbackContext) -> None:
    balance = 0  # Default balance
    usr_lng = await user_language(update.effective_user.id)
    try:
        current_user = await sync_to_async(UserData.objects.filter(id=update.effective_user.id).first)()

        if not current_user:
            await check_create_account(update)
        else:
            balance = current_user.balance

        await update.message.reply_text(
            text=texts[usr_lng]["textBalance"].format(balance, texts[usr_lng]["textPriceUnit"]),
            reply_markup=buttons[usr_lng]["back_menu_markup"])
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(texts[usr_lng]["textError"], reply_markup=buttons[usr_lng]["back_menu_markup"])
        logger.error(f"Error in user_balance function: {e}")


async def user_balance_from_call_back(update: Update, query: CallbackQuery) -> None:
    balance = 0  # Default balance
    usr_lng = await user_language(update.effective_user.id)
    try:
        current_user = await sync_to_async(UserData.objects.filter(id=query.from_user.id).first)()

        if not current_user:
            await check_create_account(update)
        else:
            balance = current_user.balance

        await query.edit_message_text(
            text=texts[usr_lng]["textBalance"].format(balance, texts[usr_lng]["textPriceUnit"]),
            reply_markup=buttons[usr_lng]["back_menu_markup"])
    except Exception as e:
        await query.edit_message_text(texts[usr_lng]["textError"],
                                      reply_markup=buttons[usr_lng]["back_menu_markup"])
        logger.error(f"Error in user_balance_from_call_back function: {e}")


# endregion


# Todo: function that return purchased products
# region Manage account

async def account_menu_call_back(query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)
    full_name = f"{query.from_user.first_name or ''} {query.from_user.last_name or ''}".strip()
    try:
        await query.edit_message_text(
            text=texts[usr_lng]["textAccountMenu"].format(full_name),
            reply_markup=buttons[usr_lng]["account_keys_markup"],
        )
    except Exception as e:
        await query.edit_message_text(texts[usr_lng]["textError"],
                                      reply_markup=buttons[usr_lng]["back_menu_markup"])
        logger.error(f"Error in menu_from_callback function: {e}")


async def account_info(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    user_data = await sync_to_async(UserData.objects.filter(id=user_id).first)()
    usr_lng = await user_language(user_id)

    if not user_data:
        await query.edit_message_text(text=texts[usr_lng]["textNotUser"],
                                      reply_markup=buttons[usr_lng]["back_to_acc_markup"])
        return

    await query.edit_message_text(text=texts[usr_lng]["textAccInfo"].format(
        user_data.username,
        (user_data.first_name or "") + (user_data.last_name or ""),
        user_data.balance,
        texts[usr_lng]["textPriceUnit"]),
        reply_markup=buttons[usr_lng]["back_to_acc_markup"])


async def account_transactions(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    usr_lng = await user_language(user_id)
    try:
        # Fetch the last 10 items ordered by -paid_time
        user_transaction: Transactions = await sync_to_async(
            lambda: list(
                Transactions.objects.filter(user_id=user_id, is_paid=True)
                .order_by('-paid_time')[:number_of_transaction]
            )
        )()

        if not user_transaction:
            await query.edit_message_text(text=texts[usr_lng]["textNoTransaction"],
                                          reply_markup=buttons[usr_lng]["back_to_acc_markup"])
            return

        result_data = texts[usr_lng]["textTransaction"]
        for t in user_transaction:
            result_data += texts[usr_lng]["textTransactionDetail"].format(t.amount, texts[usr_lng]["textPriceUnit"],
                                                                          t.paid_time)

        await query.edit_message_text(text=result_data, reply_markup=buttons[usr_lng]["back_to_acc_markup"])

    except Exception as e:
        logger.error(f"Error in account_info function: {e}")


# Create a user account if it doesn't exist
async def check_create_account(update: Update) -> None:
    user_id = update.effective_user.id
    usr_lng = await user_language(user_id)
    found: bool = await sync_to_async(UserData.objects.filter(id=user_id).exists)()

    if not found:
        try:
            first_name = update.effective_user.first_name or None
            last_name = update.effective_user.last_name or None
            username = update.effective_user.username or None

            new_user = UserData(
                id=update.effective_user.id,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )
            await sync_to_async(new_user.save)()
        except Exception as e:
            await update.message.reply_text(texts[usr_lng]["textError"])
            logger.error(f"Error in check_create_account function: {e}")


async def change_user_language(query: CallbackQuery):
    user = await sync_to_async(UserData.objects.filter(id=query.from_user.id).first)()

    try:
        found = False
        for k in texts.keys():
            if found:
                user.language = k
                found = False
                break
            if k == user.language:
                found = True
        if found:
            user.language = lang1
    except:
        logger.error("can't find next language in change language")
        user.language = lang1

    await sync_to_async(user.save)()
    language_cache[user.id] = (user.language, timezone.now().date())

    await query.edit_message_text(text=texts[user.language]["textMenu"],
                                  reply_markup=buttons[user.language]['main_menu_markup'])


# Call this after successful payment
async def charge_account(user_id: str, chat_id: str, amount: int, transaction_code: int):
    user_id: int = int(user_id)
    usr_lng = await user_language(user_id, False)

    transaction: Transactions = await sync_to_async(
        Transactions.objects.filter(user_id=user_id,
                                    transaction_code__exact=transaction_code,
                                    is_delete=False).first)()

    if not transaction or transaction.is_paid or transaction.is_expired():  # double check :)
        return False

    current_user: UserData = await sync_to_async(UserData.objects.filter(id=user_id).first)()
    current_user.balance += amount

    await sync_to_async(current_user.save)()
    await sync_to_async(transaction.mark_as_paid)()

    # send status to user
    bot = await sync_to_async(Bot)(token=token)
    await send_message_with_retry(bot=bot,
                                  chat_id=chat_id,
                                  text=texts[usr_lng]["textChargeAccount"].format(amount,
                                                                                  texts[usr_lng]["textPriceUnit"]), )

    return True


# endregion


# region ConversationHandler
# Deposit money conversation handler
async def deposit_money(update: Update, context: CallbackContext):
    usr_lng = await user_language(update.effective_user.id)
    await update.message.reply_text(text=texts[usr_lng]["textAmount"],
                                    reply_markup=buttons[usr_lng]["back_menu_markup"])
    await update.message.delete()
    return ENTER_AMOUNT


# Deposit money from CallbackQuery
async def deposit_money_from_callback(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query
    usr_lng = await user_language(query.from_user.id)
    if query.data != deposit_cb:
        return ConversationHandler.END
    await query.edit_message_text(text=texts[usr_lng]["textAmount"], reply_markup=buttons[usr_lng]["back_menu_markup"])

    return ENTER_AMOUNT


async def capture_amount(update: Update, context: CallbackContext):
    global bot_username
    # await context.bot.delete_message(update.effective_chat.id, update.effective_message.id - 1)
    user_input = update.message.text
    user_id = update.effective_user.id
    usr_lng = await user_language(user_id)

    try:
        amount = int(user_input)
        '''
        Todo : redirect to psp then redirect to bot, no need for extra pages.
        Instead of call charge_account, I need to send a link
        to payment page that created by Django and if successful, call charge_account.
        After payment done, a pop up to open telegram app desktop or mobile.
        charge_account update database and send message to telegram
        '''
        chat_id = update.effective_chat.id
        await check_create_account(update)

        # create a new transaction
        transaction = Transactions(user_id=user_id, amount=amount)
        await sync_to_async(transaction.save)()
        transaction.transaction_code = transaction.id + 1_000_000
        await sync_to_async(transaction.save)()

        if not bot_username:
            bot_username = context.bot.username
        # print(bot_username)

        pay_key = [[InlineKeyboardButton(text=texts[usr_lng]["textPayButton"], url=payment_url.format(chat_id,
                                                                                                      user_id, amount,
                                                                                                      bot_link.format(
                                                                                                          bot_username),
                                                                                                      transaction.transaction_code))]]

        pay_key_markup = InlineKeyboardMarkup(pay_key)

        await update.message.reply_text(text=texts[usr_lng]["textPaymentLink"],
                                        reply_markup=pay_key_markup)
        # await charge_account(update.effective_user.id, update.effective_chat.id, amount)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text(texts[usr_lng]["textInvalidAmount"],
                                        reply_markup=buttons[usr_lng]["back_menu_markup"])
        return ENTER_AMOUNT
    except Exception as e:
        logger.error(f"Error in capture_amount function: {e}")
    finally:
        await update.message.delete()


async def cancel_back_to_menu(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query
    await query.answer()
    await menu_from_callback(query)
    # print("Ending conversation...")  # Debug log
    return ConversationHandler.END


# endregion


# region Products
async def get_name(user_lang: str, current_object) -> str:
    current_name = current_object.name  # default is first language "en"
    try:
        if user_lang != lang1:  # name_<your language from setting.py>
            current_name = eval(f"current_object.name_{user_lang}")
            if not current_name:
                logger.error(
                    f"name {current_object.name} for language {user_lang} not founded return {current_object.name}")
                return current_object.name
        return current_name
    except:
        logger.error("language not founded return name base on lang1")
        return current_object.name


async def product_categories(query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)

    # Fetch categories asynchronously
    categories = await sync_to_async(list)(Category.objects.all())

    if not categories:
        await query.edit_message_text(text=texts[usr_lng]["textNotFound"],
                                      reply_markup=buttons[usr_lng]["back_menu_markup"])
        return  # Ensure the function exits here if no categories are found
    try:
        # Create buttons for categories
        temp_keys = []
        for i in range(0, len(categories), categories_in_row):
            row = await asyncio.gather(
                *[get_name(usr_lng, cat) for cat in categories[i:i + categories_in_row]]
            )
            temp_keys.append(
                [InlineKeyboardButton(name, callback_data=f"{select_category_cb}_{cat.id}") for name, cat in
                 zip(row, categories[i:i + categories_in_row])]
            )

        temp_keys.append(
            [InlineKeyboardButton(texts[usr_lng]["buttonBackMainMenu"], callback_data=main_menu_cb)])  # Add back button
        temp_reply_markup = InlineKeyboardMarkup(temp_keys)

        await query.edit_message_text(text=texts[usr_lng]["textProductCategories"], reply_markup=temp_reply_markup)
    except Exception as e:
        # await query.edit_message_text(textError, reply_markup=back_menu_markup)
        logger.error(f"Error in payment function: {e}")


# Todo: Show available product only
async def products(query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)
    try:
        # Extract category ID from callback data
        cat_id: int = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(texts[usr_lng]["textInvalidCategory"], show_alert=True)
        return

    # Fetch products asynchronously
    all_products = await sync_to_async(list)(Product.objects.filter(category__id=cat_id))

    if not all_products:
        await query.edit_message_text(text=texts[usr_lng]["textNoProductFound"],
                                      reply_markup=buttons[usr_lng]["back_to_cats_markup"])
        return

    try:
        # Create buttons for products
        temp_keys = []
        for i in range(0, len(all_products), products_in_row):
            # Gather the product names asynchronously
            names = await asyncio.gather(
                *[get_name(usr_lng, prod) for prod in all_products[i:i + products_in_row]]
            )
            # Create a row of InlineKeyboardButtons
            row = [
                InlineKeyboardButton(name, callback_data=f"{select_product_cb}_{prod.id}")
                for name, prod in zip(names, all_products[i:i + products_in_row])
            ]
            temp_keys.append(row)

        temp_keys.append(
            [InlineKeyboardButton(texts[usr_lng]["buttonBackMainMenu"], callback_data=main_menu_cb)])  # Add back button
        temp_keys.append([InlineKeyboardButton(texts[usr_lng]["textBackButton"], callback_data=categories_cb)])
        temp_reply_markup = InlineKeyboardMarkup(temp_keys)

        # Get category name
        current_cat: Category = await sync_to_async(Category.objects.filter(id=cat_id, is_delete=False).first)()
        cat_name = ""
        if current_cat:
            cat_name = await get_name(usr_lng, current_cat) + " "

        await query.edit_message_text(text=texts[usr_lng]["textProductList"].format(cat_name),
                                      reply_markup=temp_reply_markup)
    except Exception as e:
        # await query.edit_message_text(textError, reply_markup=back_menu_markup)
        logger.error(f"Error in payment function: {e}")


async def product_payment_detail(query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)

    try:
        # Extract product ID from callback data
        prod_id: int = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(texts[usr_lng]["textInvalidProduct"], show_alert=True)
        return

    # Fetch product asynchronously
    product_detail = await sync_to_async(
        ProductDetail.objects.filter(
            product_id=prod_id, is_purchased=False
        ).select_related('product__category').first
    )()

    if not product_detail:
        await query.answer(texts[usr_lng]["textProductSoldOut"], show_alert=True)
        return

    try:
        # Create inline keyboard buttons
        temp_keys = [
            [InlineKeyboardButton(texts[usr_lng]["textPayButton"],
                                  callback_data=f'{payment_cb}_{product_detail.product.price}_{product_detail.product.id}')],
            [InlineKeyboardButton(texts[usr_lng]["textBackButton"],
                                  callback_data=f'{select_category_cb}_{product_detail.product.category.id}')],
        ]
        temp_reply_markup = InlineKeyboardMarkup(temp_keys)

        # Edit message to show product details
        await query.edit_message_text(
            text=texts[usr_lng]["textPurchaseBill"].format(await get_name(usr_lng, product_detail.product),
                                                           product_detail.product.price,
                                                           texts[usr_lng]["textPriceUnit"]),
            reply_markup=temp_reply_markup
        )
    except Exception as e:
        # await query.edit_message_text(textError, reply_markup=back_menu_markup)
        logger.error(f"Error in product_payment_detail function: {e}")


async def payment(update: Update, context: CallbackContext, query: CallbackQuery):
    usr_lng = await user_language(query.from_user.id)

    try:
        # Extract product ID from callback data
        payment_amount: int = int(query.data.split('_')[1])
        prod_id: int = int(query.data.split('_')[2])
    except (IndexError, ValueError):
        await query.answer(texts[usr_lng]["textInvalidPaymentAmount"], show_alert=True)
        return

    current_user = await sync_to_async(UserData.objects.filter(id=update.effective_user.id).first)()

    if not current_user:
        await query.answer(text=texts[usr_lng]["textNotUser"], show_alert=True)
        return
    if current_user.balance < payment_amount:
        await query.answer(text=texts[usr_lng]["textNotEnoughMoney"], show_alert=True)
        return

    product: ProductDetail = await sync_to_async(
        ProductDetail.objects.filter(product_id=prod_id, is_purchased=False).first)()

    if not product:
        await query.answer(text=texts[usr_lng]["textProductSoldOut"], show_alert=True)
        return

    try:
        current_user.balance -= payment_amount
        product.is_purchased = True
        product.buyer = current_user
        product.purchase_date = timezone.now()

        await sync_to_async(product.save)()  # first update product detail
        await sync_to_async(current_user.save)()  # then update balance

        await send_message_with_retry(bot=context.bot,
                                      chat_id=update.effective_chat.id,
                                      text=texts[usr_lng]["textProductDetail"].format(product.details))
        # await query.delete_message()
    except Exception as e:
        await update.message.reply_text(texts[usr_lng]["textError"], reply_markup=buttons[usr_lng]["back_menu_markup"])
        logger.error(f"Error in payment function: {e}")


# endregion


# region Handlers
async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query: CallbackQuery = update.callback_query
    query_data = query.data

    if query_data == main_menu_cb:  # Main Menu
        await menu_from_callback(query)
    elif query_data == balance_cb:  # User Balance
        await user_balance_from_call_back(update, query)
    elif query_data == account_menu_cb:  # Account Menu
        await account_menu_call_back(query)
    elif query_data == transactions_cb:  # User Transactions
        await account_transactions(query)
    elif query_data == account_info_cb:  # User Account Info
        await account_info(query)
    elif query_data == categories_cb:  # Product Categories
        await product_categories(query)
    elif query_data == change_lang_cb:  # Product Categories
        await change_user_language(query)
    elif query_data.startswith(f"{select_category_cb}_"):  # Selected category
        await products(query)
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


# For unknown commands and texts
async def delete_message(update: Update, context: ContextTypes.DEFAULT_TYPE):
    await update.message.delete()


# Todo: use cachetools for an LRU (Least Recently Used) cache to manage memory effectively.
async def user_language(user_id: int, cache: bool = True):
    date_now = timezone.now().date()
    if user_id not in language_cache or not cache:
        user = await sync_to_async(UserData.objects.filter(id=user_id).first)()
        if not user:
            language_cache[user_id] = (lang1, date_now)
            return lang1
        language_cache[user_id] = (user.language, date_now)
        # print(language_cache)
        # print(sys.getsizeof(language_cache))
        return user.language
    else:
        # reset aging
        # language_cache[user_id] = (language_cache[user_id][0], date_now)
        return language_cache[user_id][0]


async def send_message_with_retry(bot, chat_id, text, retry=5):
    for attempt in range(retry):
        try:
            return await bot.send_message(chat_id=chat_id, text=text)
        except Exception as e:
            if attempt < retry - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed to send message after {retry} attempts: {e}")
                return None


# Main function
def main() -> None:
    app = Application.builder().token(token).build()

    handlers = [
        CommandHandler("start", start_menu),  # Check account or create only here
        CommandHandler("menu", start_menu),
        CommandHandler("balance", user_balance),
        ConversationHandler(
            entry_points=[
                CommandHandler("deposit", deposit_money),
                CallbackQueryHandler(deposit_money_from_callback, pattern=f"^{deposit_cb}$"),
            ],
            states={
                ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_amount)],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_back_to_menu),
                CallbackQueryHandler(cancel_back_to_menu, pattern=f"^{main_menu_cb}$"),  # For callback button
            ],
        ),
        MessageHandler(filters.TEXT, delete_message),  # Performance issue
        CallbackQueryHandler(callback_query_handler),
    ]

    app.add_handlers(handlers)

    app.add_error_handler(error_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
