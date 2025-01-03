from django.shortcuts import render, redirect
from django.urls import reverse
from django.http import Http404
from django.views import View
from .models import Transactions
from .send_message_telegram import charge_account
import logging

logger = logging.getLogger(__name__)

# Set up logging
logging.basicConfig(
    filename='./payment_logs.log',
    format='%(asctime)s - %(name)s - %(levelname)s - %(message)s',
    level=logging.WARN
)


class PaymentView(View):
    def get(self, request):
        # Handles payment confirmation page
        try:
            user_id = request.GET.get('user_id')
            chat_id = request.GET.get('chat_id')
            amount = int(request.GET.get('amount'))
            bot_link = request.GET.get('bot_link')
            transaction_code = request.GET.get('transaction')
        except (ValueError, TypeError):
            logger.error("Invalid parameters in GET request.")
            raise Http404

        # Check if the transaction is valid and not repetitive
        try:
            transaction = Transactions.objects.filter(
                user_id=user_id, transaction_code__exact=transaction_code, is_delete=False, is_paid=False
            ).first()

            if not transaction or transaction.is_expired():
                logger.warning(
                    f"Invalid or expired transaction: {transaction_code}")
                return redirect(f"{reverse('payment_status')}?bot_link={bot_link}&status=failed")

        except Exception as e:
            logger.error(f"Error fetching transaction: {e}")
            return redirect(f"{reverse('payment_status')}?bot_link={bot_link}&status=failed")

        # Render confirmation page
        context = {
            'title': "Payment Confirmation",
            'user_id': user_id,
            'chat_id': chat_id,
            'amount': amount,
            'bot_link': bot_link,
            'transaction_code': transaction_code,
            'action': reverse('payment_confirmation'),
        }
        return render(request, 'payment/confirm.html', context)

    def post(self, request):
        # Handles charging the account
        bot_link = request.POST.get('bot_link', "")
        status = "failed"
        try:
            user_id = request.POST.get('user_id')
            chat_id = request.POST.get('chat_id')
            amount = int(request.POST.get('amount'))
            transaction_code = request.POST.get('transaction')

            # Call synchronous function to charge the account
            res = charge_account(user_id, chat_id, amount, transaction_code)
            if res:
                status = "success"

        except (ValueError, TypeError) as e:
            logger.error(f"Invalid parameters in POST request: {e}")
        except Exception as e:
            logger.error(f"Error during account charging: {e}")

        # Redirect to status page
        return redirect(f"{reverse('payment_status')}?bot_link={bot_link}&status={status}")


class PaymentStatusView(View):
    def get(self, request):
        # Handles rendering the payment status page
        bot_link = request.GET.get('bot_link')
        status = request.GET.get('status', 'failed')

        context = {
            'title': "Payment Status",
            'payment_status': "Successful" if status == 'success' else "Failed",
            'bot_link': bot_link,
        }
        return render(request, 'payment/status.html', context)
