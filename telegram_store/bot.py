# region bot settings
# Todo: manage import when call charge account
if __name__ == "__main__":
    from bot_settings import *
else:
    textChargeAccount = "Your account has been successfully charged {} {}."  # amount, price unit
    textPriceUnit = "dollar"
# endregion


# region Django Imports
import os
import django
from django.utils import timezone

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_store.settings')
django.setup()

from users.models import UserData
from payment.models import Transitions

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


# region global variables

# Define states
ENTER_AMOUNT = 1

token = config("TOKEN")


# endregion


# region Menu

async def start_menu(update: Update, context: CallbackContext) -> None:  # active command is /start
    try:
        await check_create_account(update)  # Create a user if not exist
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=textStart.format(update.effective_user.username),
            reply_markup=main_menu_markup,
        )
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(textError, reply_markup=back_menu_markup)
        logger.error(f"Error in start_menu function: {e}")


async def menu_from_callback(query: CallbackQuery) -> None:
    try:
        await query.edit_message_text(
            text=textMenu,
            reply_markup=main_menu_markup,
        )
    except Exception as e:
        await query.edit_message_text(textError,
                                      reply_markup=main_menu_markup)
        logger.error(f"Error in menu_from_callback function: {e}")


# endregion


# region Balance

async def user_balance(update: Update, context: CallbackContext) -> None:
    balance = 0  # Default balance
    try:
        current_user = await sync_to_async(UserData.objects.filter(id=update.effective_user.id).first)()

        if not current_user:
            await check_create_account(update)
        else:
            balance = current_user.balance

        await update.message.reply_text(text=textBalance.format(balance, textPriceUnit),
                                        reply_markup=back_menu_markup)
        await update.message.delete()
    except Exception as e:
        await update.message.reply_text(textError)
        logger.error(f"Error in user_balance function: {e}")


async def user_balance_from_call_back(update: Update, query: CallbackQuery) -> None:
    balance = 0  # Default balance
    try:
        current_user = await sync_to_async(UserData.objects.filter(id=query.from_user.id).first)()

        if not current_user:
            await check_create_account(update)
        else:
            balance = current_user.balance

        await query.edit_message_text(text=textBalance.format(balance, textPriceUnit),
                                      reply_markup=back_menu_markup)
    except Exception as e:
        await query.edit_message_text(textError,
                                      reply_markup=back_menu_markup)
        logger.error(f"Error in user_balance_from_call_back function: {e}")


# endregion


# region Manage account

# Todo: function that return purchased products
async def account_menu_call_back(query: CallbackQuery):
    try:
        await query.edit_message_text(
            text=textAccountMenu.format(query.from_user.username),
            reply_markup=account_keys_markup,
        )
    except Exception as e:
        await query.edit_message_text(textError,
                                      reply_markup=back_menu_markup)
        logger.error(f"Error in menu_from_callback function: {e}")


async def account_info(query: CallbackQuery) -> None:
    user_id = query.from_user.id
    user_data = await sync_to_async(UserData.objects.filter(id=user_id).first)()

    if not user_data:
        await query.edit_message_text(text=textNotUser, reply_markup=back_to_acc_markup)
        return

    await query.edit_message_text(text=textAccInfo.format(
        user_data.username,
        (user_data.first_name or "") + (user_data.last_name or ""),
        user_data.balance,
        textPriceUnit),
        reply_markup=back_to_acc_markup)


async def account_transitions(query: CallbackQuery) -> None:
    try:
        # Fetch the last 10 items ordered by -paid_time
        user_transitions: Transitions = await sync_to_async(
            lambda: list(
                Transitions.objects.filter(user_id=query.from_user.id, is_paid=True)
                .order_by('-paid_time')[:5]
            )
        )()

        if not user_transitions:
            await query.edit_message_text(text=textNoTransition, reply_markup=back_to_acc_markup)
            return

        result_data = textTransitions
        for t in user_transitions:
            result_data += f"Amount: {t.amount} {textPriceUnit}\nDate: {t.paid_time}\n\n"

        await query.edit_message_text(text=result_data, reply_markup=back_to_acc_markup)

    except Exception as e:
        logger.error(f"Error in account_info function: {e}")


# Create a user account if it doesn't exist
async def check_create_account(update: Update) -> None:
    user_id = update.effective_user.id

    found: bool = await sync_to_async(UserData.objects.filter(id=user_id).exists)()

    if not found:
        try:
            first_name = update.effective_user.first_name or None
            last_name = update.effective_user.last_name or None
            username = update.effective_user.username

            new_user = UserData(
                id=update.effective_user.id,
                first_name=first_name,
                last_name=last_name,
                username=username,
            )
            await sync_to_async(new_user.save)()
        except Exception as e:
            await update.message.reply_text(textError)
            logger.error(f"Error in check_create_account function: {e}")


# Call this after successful payment
async def charge_account(user_id: str, chat_id: str, amount: int, transition_code: int):
    user_id: int = int(user_id)

    transition: Transitions = await sync_to_async(
        Transitions.objects.filter(user_id=user_id,
                                   transitions_code__exact=transition_code,
                                   is_delete=False).first)()

    if not transition or transition.is_paid or transition.is_expired():  # double check :)
        return False

    current_user: UserData = await sync_to_async(UserData.objects.filter(id=user_id).first)()
    current_user.balance += amount

    await sync_to_async(current_user.save)()
    await sync_to_async(transition.mark_as_paid)()

    # Todo: retry needed
    # send status to user
    bot = await sync_to_async(Bot)(token=token)
    await bot.send_message(chat_id=chat_id,
                           text=textChargeAccount.format(amount, textPriceUnit),
                           reply_markup=None)

    return True


# endregion


# region ConversationHandler
# Deposit money conversation handler
async def deposit_money(update: Update, context: CallbackContext):
    await update.message.reply_text(text=textAmount, reply_markup=back_menu_markup)
    await update.message.delete()
    return ENTER_AMOUNT


# Deposit money from CallbackQuery
async def deposit_money_from_callback(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query
    if query.data != "deposit":
        return ConversationHandler.END
    await query.edit_message_text(text=textAmount, reply_markup=back_menu_markup)

    return ENTER_AMOUNT


async def capture_amount(update: Update, context: CallbackContext):
    # await context.bot.delete_message(update.effective_chat.id, update.effective_message.id - 1)
    user_input = update.message.text
    try:
        amount = int(user_input)
        '''
        Todo Done :)
        Instead of call charge_account, I need to send a link
        to payment page that created by Django and if successful, call charge_account.
        After payment done, a pop up to open telegram app desktop or mobile.
        charge_account update database and send message to telegram
        '''
        chat_id = update.effective_chat.id
        user_id = update.effective_user.id
        await check_create_account(update)

        # create a new transition
        transitions = Transitions(user_id=user_id, amount=amount)
        await sync_to_async(transitions.save)()
        transitions.transitions_code = transitions.id + 1_000_000
        await sync_to_async(transitions.save)()

        pay_key = [[InlineKeyboardButton(text=textPayButton, url=payment_url.format(chat_id,
                                                                                    user_id, amount, bot_link,
                                                                                    transitions.transitions_code))]]

        pay_key_markup = InlineKeyboardMarkup(pay_key)

        await update.message.reply_text(text=textPaymentLink,
                                        reply_markup=pay_key_markup)
        # await charge_account(update.effective_user.id, update.effective_chat.id, amount)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text(textInvalidAmount,
                                        reply_markup=back_menu_markup)
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
async def product_categories(query: CallbackQuery):
    # Fetch categories asynchronously
    categories = await sync_to_async(list)(Category.objects.all())

    if not categories:
        await query.edit_message_text(text=textNotFound, reply_markup=back_menu_markup)
        return  # Ensure the function exits here if no categories are found

    # Create buttons for categories
    temp_keys = [
        [InlineKeyboardButton(cat.name, callback_data=f"category_{cat.id}") for cat in
         categories[i:i + categories_in_row]]
        for i in range(0, len(categories), categories_in_row)
    ]
    temp_keys.append(back_menu_key[0])  # Add back button
    temp_reply_markup = InlineKeyboardMarkup(temp_keys)

    await query.edit_message_text(text=textProductCategories, reply_markup=temp_reply_markup)


async def products(query: CallbackQuery):
    try:
        # Extract category ID from callback data
        cat_id: int = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(textInvalidCategory, show_alert=True)
        return

    # Fetch products asynchronously
    all_products = await sync_to_async(list)(Product.objects.filter(category__id=cat_id))

    if not all_products:
        await query.edit_message_text(text=textNoProductFound, reply_markup=back_to_cats_markup)
        return

    # Create buttons for products
    temp_keys = [
        [InlineKeyboardButton(prod.name, callback_data=f"product_{prod.id}") for prod in all_products[i:i + products_in_row]]
        for i in range(0, len(all_products), products_in_row)
    ]
    temp_keys.append(back_menu_key[0])  # Add back button
    temp_keys.append([InlineKeyboardButton(textBackButton, callback_data='categories')])
    temp_reply_markup = InlineKeyboardMarkup(temp_keys)

    # Get category name
    current_cat: Category = await sync_to_async(Category.objects.filter(id=cat_id, is_delete=False).first)()
    cat_name = "The"
    if current_cat:
        cat_name = current_cat.name
    # print(cat_name)

    await query.edit_message_text(text=textProductList.format(cat_name), reply_markup=temp_reply_markup)


async def product_payment_detail(query: CallbackQuery):
    try:
        # Extract product ID from callback data
        prod_id: int = int(query.data.split('_')[1])
    except (IndexError, ValueError):
        await query.answer(textInvalidProduct, show_alert=True)
        return

    # Fetch product asynchronously
    product_detail = await sync_to_async(
        ProductDetail.objects.filter(
            product_id=prod_id, is_purchased=False
        ).select_related('product__category').first
    )()

    if not product_detail:
        await query.answer(textProductSoldOut, show_alert=True)
        return

    # Create inline keyboard buttons
    temp_keys = [
        [InlineKeyboardButton('Pay', callback_data=f'payment_{product_detail.price}_{product_detail.product.id}')],
        [InlineKeyboardButton('Back', callback_data=f'category_{product_detail.product.category.id}')],
    ]
    temp_reply_markup = InlineKeyboardMarkup(temp_keys)

    # Edit message to show product details
    await query.edit_message_text(
        text=textPurchaseBill.format(product_detail.product.name, product_detail.price, textPriceUnit),
        reply_markup=temp_reply_markup
    )


async def payment(update: Update, context: CallbackContext, query: CallbackQuery):
    try:
        # Extract product ID from callback data
        payment_amount: int = int(query.data.split('_')[1])
        prod_id: int = int(query.data.split('_')[2])
    except (IndexError, ValueError):
        await query.answer(textInvalidPaymentAmount, show_alert=True)
        return

    current_user = await sync_to_async(UserData.objects.filter(id=update.effective_user.id).first)()

    if not current_user:
        await query.answer(text=textNotUser, show_alert=True)
        return
    if current_user.balance < payment_amount:
        await query.answer(text=textNotEnoughMoney, show_alert=True)
        return

    product: ProductDetail = await sync_to_async(
        ProductDetail.objects.filter(product_id=prod_id, is_purchased=False).first)()

    if not product:
        await query.answer(text=textProductSoldOut, show_alert=True)
        return

    current_user.balance -= payment_amount
    product.is_purchased = True
    product.buyer = current_user
    product.purchase_date = timezone.now()

    await sync_to_async(product.save)()
    await sync_to_async(current_user.save)()

    await context.bot.send_message(text=textProductDetail.format(product.details),
                                   chat_id=update.effective_chat.id)
    # await query.delete_message()


# endregion


# region Handlers
async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query: CallbackQuery = update.callback_query
    query_data = query.data
    # Todo: convert it to switch case
    if query_data == "main_menu":  # Main Menu
        await menu_from_callback(query)
    elif query_data == "bala":  # User Balance
        await user_balance_from_call_back(update, query)
    elif query_data == "acc":  # Account Menu
        await account_menu_call_back(query)
    elif query_data == "trans_list":  # User Transitions
        await account_transitions(query)
    elif query_data == "acc_info":  # User Account Info
        await account_info(query)
    elif query_data == "categories":
        await product_categories(query)
    elif query_data.startswith('category_'):  # selected category
        await products(query)
    elif query_data.startswith('product_'):  # selected category
        await product_payment_detail(query)
    elif query_data.startswith('payment_'):  # selected category
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
                CallbackQueryHandler(deposit_money_from_callback, pattern="^deposit$"),
            ],
            states={
                ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_amount)],
            },
            fallbacks=[
                CommandHandler("cancel", cancel_back_to_menu),
                CallbackQueryHandler(cancel_back_to_menu, pattern="^main_menu$"),  # For callback button
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
