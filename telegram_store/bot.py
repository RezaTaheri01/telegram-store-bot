# region Django Imports
import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_store.settings')
django.setup()

from users.models import UserData
from payment.models import Transitions
# endregion


# region Telegram Imports
from asgiref.sync import sync_to_async
from telegram import Update, Bot, InlineKeyboardButton, InlineKeyboardMarkup, CallbackQuery
from telegram.ext import (
    Application,
    CommandHandler,
    CallbackQueryHandler,
    ConversationHandler,
    MessageHandler,
    filters,
    CallbackContext,
)
from decouple import config
# endregion

import logging

# region Logs

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
# Keyboard layouts
main_menu_keys = [
    [InlineKeyboardButton("My Account", callback_data="account"),
     InlineKeyboardButton("My Balance", callback_data="balance")],
    [InlineKeyboardButton("Deposit", callback_data="deposit")],
]
main_menu_markup = InlineKeyboardMarkup(main_menu_keys)

back_menu_key = [
    [InlineKeyboardButton("Back to menu", callback_data="main_menu")],
]
back_menu_markup = InlineKeyboardMarkup(back_menu_key)

# Define states
ENTER_AMOUNT = 1

# Text messages
priceUnit = "dollar"
textStart = "Hello, {}! How can I assist you today?"
textBalance = "Your current balance is {} {}."
textAmount = "Please enter the amount:"
textChargeAccount = "Your account has been successfully charged {} {}."
textPayment = "Your payment link is ready."
payment_url = "http://127.0.0.1:8000/payment/confirm/?chat_id={}&user_id={}&amount={}&bot_link={}&transition={}"
bot_link = "https://t.me/gameStorePersiaBot"

token = config("TOKEN")


# endregion


# region Menu
async def start_menu(update: Update, context: CallbackContext) -> None:
    try:
        await check_create_account(update)  # Create a user if not exist
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=textStart.format(update.effective_user.username),
            reply_markup=main_menu_markup,
        )
    except Exception as e:
        await update.message.reply_text("Something went wrong :(")
        logger.error(f"Error in start_menu function: {e}")


async def menu_from_callback(query: CallbackQuery) -> None:
    try:
        await query.edit_message_text(
            text=textStart.format(query.from_user.username),
            reply_markup=main_menu_markup,
        )
    except Exception as e:
        await query.edit_message_text("Something went wrong :(",
                                      reply_markup=None)
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

        await update.message.reply_text(text=textBalance.format(balance, priceUnit),
                                        reply_markup=back_menu_markup)
    except Exception as e:
        await update.message.reply_text("Something went wrong :(")
        logger.error(f"Error in user_balance function: {e}")


async def user_balance_from_call_back(update: Update, query: CallbackQuery) -> None:
    balance = 0  # Default balance
    try:
        current_user = await sync_to_async(UserData.objects.filter(id=query.from_user.id).first)()

        if not current_user:
            await check_create_account(update)
        else:
            balance = current_user.balance

        await query.edit_message_text(text=textBalance.format(balance, priceUnit),
                                      reply_markup=back_menu_markup)
    except Exception as e:
        await query.edit_message_text("Something went wrong :(",
                                      reply_markup=None)
        logger.error(f"Error in user_balance_from_call_back function: {e}")


# endregion


# region Manage account
# Create a user account if it doesn't exist
async def check_create_account(update: Update) -> None:
    user_id = update.effective_user.id

    user_data = await sync_to_async(UserData.objects.filter(id=user_id).first)()

    if not user_data:
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
            await update.message.reply_text("Something went wrong :(")
            logger.error(f"Error in check_create_account function: {e}")


# Call this after successful payment
async def charge_account(user_id: int, chat_id: int, amount: float, transition_code: int):
    transition: Transitions = await sync_to_async(
        Transitions.objects.filter(user_id=user_id, transitions_code__exact=transition_code).first)()
    if not transition or transition.is_paid:
        return False

    current_user: UserData = await sync_to_async(UserData.objects.filter(id=user_id).first)()
    current_user.balance += amount

    await sync_to_async(current_user.save)()
    await sync_to_async(transition.mark_as_paid)()

    # Todo: retry needed
    # send status to user
    bot = await sync_to_async(Bot)(token=token)
    await bot.send_message(chat_id=chat_id,
                           text=textChargeAccount.format(amount, priceUnit),
                           reply_markup=back_menu_markup)

    return True


# endregion


# region ConversationHandler
# Deposit money conversation handler
async def deposit_money(update: Update, context: CallbackContext):
    await update.message.reply_text(text=textAmount, reply_markup=back_menu_markup)
    return ENTER_AMOUNT


# Deposit money from CallbackQuery
async def deposit_money_from_callback(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query
    if query.data != "deposit":
        return ConversationHandler.END
    await query.edit_message_text(text=textAmount, reply_markup=back_menu_markup)

    return ENTER_AMOUNT


async def capture_amount(update: Update, context: CallbackContext):
    user_input = update.message.text
    try:
        amount = float(user_input)
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

        pay_key = [[InlineKeyboardButton(text="Pay", url=payment_url.format(chat_id,
                                                                            user_id, amount, bot_link,
                                                                            transitions.transitions_code))]]

        pay_key_markup = InlineKeyboardMarkup(pay_key)

        await update.message.reply_text(text=textPayment,
                                        reply_markup=pay_key_markup)
        # await charge_account(update.effective_user.id, update.effective_chat.id, amount)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a valid number:",
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
    print("Ending conversation...")  # Debug log
    return ConversationHandler.END


# endregion


async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query: CallbackQuery = update.callback_query
    await query.answer()  # Stop button animation

    query_data = query.data

    if query_data == "main_menu":
        await cancel_back_to_menu(query)
    elif query_data == "balance":
        await user_balance_from_call_back(update, query)
    elif query_data == "account":
        await query.edit_message_text(text="Account section is under development.",
                                      reply_markup=back_menu_markup)


# Global Error Handler
async def error_handler(update: Update, context: CallbackContext):
    try:
        logger.error(msg="Exception while handling an update:",
                     exc_info=context.error)

        # Notify the user (optional)
        if update and update.effective_user:
            await update.effective_message.reply_text('An error occurred. The bot will continue to work.')

    except Exception as e:
        logger.error(f"Error in error_handler: {e}")


# Main function
def main() -> None:
    app = Application.builder().token(token).build()

    handlers = [
        CommandHandler("start", start_menu),
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
        CallbackQueryHandler(callback_query_handler),
    ]

    app.add_handlers(handlers)

    app.add_error_handler(error_handler)

    app.run_polling()


if __name__ == "__main__":
    main()
