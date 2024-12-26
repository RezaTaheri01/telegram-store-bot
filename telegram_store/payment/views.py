from django.shortcuts import render

from bot import charge_account

from django.shortcuts import redirect
from django.urls import reverse
from django.http import Http404
from django.views import View

from .models import Transitions
from asgiref.sync import sync_to_async


# Todo: much more to do here:
# need to check all variable to be correct
# success page that link to telegram bot
# need a transitions db that prevent repetitive charge_account


class PaymentView(View):
    async def get(self, request):
        # Handles payment confirmation page
        try:
            user_id = request.GET.get('user_id')
            chat_id = request.GET.get('chat_id')
            amount = int(request.GET.get('amount'))
            bot_link = request.GET.get('bot_link')
            transition_code = request.GET.get('transition')
        except (ValueError, TypeError):
            raise Http404

        # Render confirmation page
        context = {
            'title': "Payment Confirmation",
            'user_id': user_id,
            'chat_id': chat_id,
            'amount': amount,
            'bot_link': bot_link,
            'transitions_code': transition_code,
            'action': reverse('payment_confirmation'),  # URL for POST request
        }

        # check if transition not repetitive
        transition: Transitions = await sync_to_async(
            Transitions.objects.filter(user_id=user_id, transitions_code__exact=transition_code,
                                       is_delete=False).first)()

        if not transition or transition.is_paid or transition.is_expired():
            return redirect(f"{reverse('payment_status')}?bot_link={bot_link}&status=failed")

        return render(request, 'payment/confirm.html', context)  # redirect to payment page

    async def post(self, request):
        # Todo: here we check transitions_code to not be paid and repetitive
        bot_link = ""
        status = "failed"
        # Handles charging the account
        try:
            user_id = request.POST.get('user_id')
            chat_id = request.POST.get('chat_id')
            amount = int(request.POST.get('amount'))
            bot_link = request.POST.get('bot_link')
            transitions_code = request.POST.get('transition')

            # Call async function to charge the account
            res: bool = await charge_account(user_id, chat_id, amount, int(transitions_code))
            if res:
                status = "success"

        except (ValueError, TypeError):
            return redirect(
                f"{reverse('payment_status')}?bot_link={bot_link}&status={status}"
            )
        except Exception as e:
            # Redirect to status page after processing the payment
            return redirect(
                f"{reverse('payment_status')}?bot_link={bot_link}&status={status}"
            )

        # Redirect to status page after processing the payment
        return redirect(
            f"{reverse('payment_status')}?bot_link={bot_link}&status={status}"
        )


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
