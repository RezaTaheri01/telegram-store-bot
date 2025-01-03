# Todo: Celery for handling this section and payback if transaction saving failed

import asyncio
from telegram import Bot
from .models import Transactions
from users.models import UserData
from bot_settings import lang1, texts
from decouple import config
from django.db import transaction as db_transaction
import logging

token = config("TOKEN")

logger = logging.getLogger(__name__)

# Set up logging
logging.basicConfig(
    filename='./payment_logs.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN  # Changed to DEBUG for more detailed logs
)


async def send_message(bot: Bot, chat_id: str, message: str, retry=3):
    for attempt in range(retry):
        try:
            return await bot.send_message(chat_id=chat_id, text=message)
        except Exception as e:
            if attempt < retry - 1:
                await asyncio.sleep(2 ** attempt)  # Exponential backoff
            else:
                logger.error(f"Failed to send message after {retry} attempts: {e}")
                return


def _user_language_sync(user_id: int):
    user = UserData.objects.filter(id=user_id).first()
    if not user:
        return lang1
    return user.language


def _charge_account_in_atomic_block(user_id, amount, transaction_code):
    # Execute all database operations in a synchronous context
    with db_transaction.atomic():
        transaction: Transactions = Transactions.objects.select_for_update().filter(
            user_id=user_id,
            transaction_code__exact=transaction_code,
            is_delete=False,
            is_paid=False
        ).first()

        if not transaction or transaction.is_expired():
            raise ValueError(f"Invalid or expired transaction: {transaction_code}")

        # Update user balance
        current_user = UserData.objects.filter(id=user_id).first()
        if not current_user:
            raise ValueError(f"User not found: {user_id}")

        current_user.balance += amount
        current_user.save()
        transaction.mark_as_paid()


def charge_account(user_id: str, chat_id: str, amount: int, transaction_code: str) -> bool:
    try:
        user_id = int(user_id)

        # Get user language
        usr_lng = _user_language_sync(user_id)

        # Perform database operations inside a synchronous atomic block
        _charge_account_in_atomic_block(user_id, amount, transaction_code)

        # Send success message
        asyncio.run(
            send_message(
                Bot(token=token),
                chat_id,
                texts[usr_lng]["textChargeAccount"].format(amount, texts[usr_lng]["textPriceUnit"]),
            )
        )

        return True

    except Exception as e:
        logger.error(f"Error in charge_account: {e}")
        return False
