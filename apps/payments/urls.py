from django.urls import path
from .views import CreatePaymentIntentView, ConfirmPaymentView, StripeWebhookView

urlpatterns = [
    path('create-intent/', CreatePaymentIntentView.as_view(), name='create-intent'),
    path('confirm/', ConfirmPaymentView.as_view(), name='confirm-payment'),
    path('webhook/', StripeWebhookView.as_view(), name='stripe-webhook'),
]
