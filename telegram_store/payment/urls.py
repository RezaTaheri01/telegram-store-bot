from django.urls import path, include
from . import views

urlpatterns = [
    path('', views.PaymentView.as_view(), name="payment_confirmation"),
    path('status/', views.PaymentStatusView.as_view(), name="payment_status"),
]
