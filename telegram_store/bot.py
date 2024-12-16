import os
import django

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_store.settings')
django.setup()

from asgiref.sync import sync_to_async
from users.models import UserData
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

# region global variables
# Keyboard layouts
keys = [
    [InlineKeyboardButton("My Account", callback_data="account"),
     InlineKeyboardButton("My Balance", callback_data="balance")],
    [InlineKeyboardButton("Deposit", callback_data="deposit")],
]
keys_markup = InlineKeyboardMarkup(keys)

cancel_key = [
    [InlineKeyboardButton("Back to menu", callback_data="menu")],
]
menu_key_markup = InlineKeyboardMarkup(cancel_key)

# Define states
ENTER_AMOUNT = 1

# Text messages
priceUnit = "dollar"
textStart = "Hey there {}, What do you want to do?"
textBalance = "Your current balance is {} {}"
textAmount = "Enter your amount:"
textChargeAccount = "Your account was charged {} {} successfully."

token = config("TOKEN")


# endregion


# region Menu
async def start_menu(update: Update, context: CallbackContext) -> None:
    try:
        await check_create_account(update)  # Create a user if not exist
        await context.bot.send_message(
            chat_id=update.effective_user.id,
            text=textStart.format(update.effective_user.username),
            reply_markup=keys_markup,
        )
    except Exception as e:
        await update.message.reply_text("Something went wrong :(")


async def menu_from_callback(query: CallbackQuery) -> None:
    try:
        await query.edit_message_text(
            text=textStart.format(query.from_user.username),
            reply_markup=keys_markup,
        )
    except Exception as e:
        await query.edit_message_text("Something went wrong :(",
                                      reply_markup=None)


# endregion


# region Balance
async def user_balance(update: Update, context: CallbackContext) -> None:
    current_user = await sync_to_async(UserData.objects.filter(id=update.effective_user.id).first)()
    balance = 0  # Default balance

    if not current_user:
        await check_create_account(update)
    else:
        balance = current_user.balance

    await update.message.reply_text(text=textBalance.format(balance, priceUnit),
                                    reply_markup=menu_key_markup)


async def user_balance_from_call_back(query: CallbackQuery) -> None:
    current_user = await sync_to_async(UserData.objects.filter(id=query.from_user.id).first)()
    await query.edit_message_text(text=textBalance.format(current_user.balance, priceUnit),
                                  reply_markup=menu_key_markup)


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


# endregion


# region ConversationHandler
# Deposit money conversation handler
async def deposit_money(update: Update, context: CallbackContext):
    await update.message.reply_text(text=textAmount, reply_markup=menu_key_markup)
    return ENTER_AMOUNT


# Deposit money from CallbackQuery
async def deposit_money_from_callback(update: Update, context: CallbackContext):
    query: CallbackQuery = update.callback_query
    await query.edit_message_text(text=textAmount, reply_markup=menu_key_markup)

    return ENTER_AMOUNT


async def capture_amount(update: Update, context: CallbackContext):
    user_input = update.message.text
    try:
        amount = float(user_input)
        '''
        Todo
        Instead of call charge_account, I need to send a link
        to payment page that created by Django and if successful, call charge_account.
        After payment done, a pop up to open telegram app desktop or mobile.
        charge_account update database and send message to telegram
        '''
        await charge_account(update.effective_user.id, update.effective_chat.id, amount)
        return ConversationHandler.END
    except ValueError:
        await update.message.reply_text("Invalid input. Please enter a valid number:",
                                        reply_markup=menu_key_markup)
        return ENTER_AMOUNT
    finally:
        await update.message.delete()


async def cancel_back_to_menu(query: CallbackQuery):
    await menu_from_callback(query)
    return ConversationHandler.END


# endregion


# Call this after successful payment
async def charge_account(user_id: int, chat_id: int, amount: float):
    current_user: UserData = await sync_to_async(UserData.objects.filter(id=user_id).first)()
    current_user.balance += amount
    await sync_to_async(current_user.save)()

    # send status to user
    bot = Bot(token=token)
    await bot.send_message(chat_id=chat_id,
                           text=textChargeAccount.format(amount, priceUnit),
                           reply_markup=menu_key_markup)


async def callback_query_handler(update: Update, context: CallbackContext) -> None:
    query: CallbackQuery = update.callback_query
    await query.answer()  # Stop button animation

    # Debugging
    print(f"Callback data received: {query.data}")

    query_data = query.data

    if query_data == "menu":
        await cancel_back_to_menu(query)
    elif query_data == "balance":
        await user_balance_from_call_back(query)
    elif query_data == "account":
        await query.edit_message_text(text="Account section is under development.",
                                      reply_markup=menu_key_markup)


# Main function
def main() -> None:
    app = Application.builder().token(token).build()

    handlers = [
        CommandHandler("start", start_menu),
        CommandHandler("menu", start_menu),
        CommandHandler("balance", user_balance),
        ConversationHandler(
            entry_points=[CommandHandler("deposit", deposit_money),
                          CallbackQueryHandler(deposit_money_from_callback, pattern="^deposit$"), ],
            states={
                ENTER_AMOUNT: [MessageHandler(filters.TEXT & ~filters.COMMAND, capture_amount)],
            },
            fallbacks=[CommandHandler("cancel", cancel_back_to_menu)],
        ),
        CallbackQueryHandler(callback_query_handler),
    ]

    app.add_handlers(handlers)
    app.run_polling()


if __name__ == "__main__":
    main()
