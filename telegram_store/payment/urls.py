from django.urls import path
from . import views

urlpatterns = [
    path('confirm/', views.PaymentView.as_view(), name="payment_confirmation"),
    path('status/', views.PaymentStatusView.as_view(), name="payment_status"),
]
