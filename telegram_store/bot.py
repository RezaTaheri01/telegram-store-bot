import os
import django
from telegram_store.settings import DATABASES, INSTALLED_APPS

os.environ.setdefault('DJANGO_SETTINGS_MODULE', 'telegram_store.settings')
django.setup()

from asgiref.sync import sync_to_async
from users.models import UserData
from telegram import Update
from telegram.ext import Application, CommandHandler, CallbackContext
from decouple import config


async def start(update: Update, context: CallbackContext) -> None:
    try:
        user_id = update.effective_user.id

        # Try to fetch the user data
        user_data = await sync_to_async(UserData.objects.filter(id=user_id).first)()

        if user_data:
            # notif existing user
            await update.message.reply_text('You already have an account')
        else:
            # create an account
            await create_account(update)
    except Exception as e:
        await update.message.reply_text('Something went wrong :(')


async def user_balance(update: Update, context: CallbackContext) -> None:
    # Ensure this is inside an async function
    current_user = await sync_to_async(UserData.objects.filter(id=update.effective_user.id).first)()
    balance = 0

    if not current_user:
        await create_account(update)
    else:
        balance = current_user.balance

    await update.message.reply_text(text=f"Your current balance is {balance}")


async def create_account(update: Update):
    try:
        # Prepare default values for new user
        first_name = update.effective_user.first_name or None
        last_name = update.effective_user.last_name or None
        username = update.effective_user.username

        # Create a new user
        new_user = UserData(
            id=update.effective_user.id,
            first_name=first_name,
            last_name=last_name,
            username=username
        )
        await sync_to_async(new_user.save)()  # Save user asynchronously
        await update.message.reply_text('Your account is created successfully')
    except Exception as e:
        await update.message.reply_text('Something went wrong :(')


def main() -> None:
    token = config("TOKEN")
    app = Application.builder().token(token).build()

    handlers: list = [
        CommandHandler("start", start),
        CommandHandler("balance", user_balance),
    ]

    app.add_handlers(handlers)

    app.run_polling()


if __name__ == '__main__':
    main()
