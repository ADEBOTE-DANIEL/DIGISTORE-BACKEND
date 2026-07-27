"""
PAYMENTS/VIEWS.PY — Stripe Integration
========================================
STEP 1 — CreatePaymentIntentView: Django creates a Stripe PaymentIntent
  server-side (secret key never leaves server), returns client_secret.

STEP 2 — React Native uses client_secret with confirmPayment() (Stripe SDK).
  Card data never touches Django.

STEP 3 — StripeWebhookView: Stripe sends a signed webhook event after payment.
  Django verifies the signature and marks the order 'paid'.
  Webhooks are trusted because they're cryptographically signed by Stripe —
  unlike a frontend request claiming "payment succeeded", which could be faked.
"""

import stripe
from django.conf import settings
from django.views.decorators.csrf import csrf_exempt
from django.utils.decorators import method_decorator
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated, AllowAny
from apps.products.models import Product
from apps.orders.models import Order, OrderItem

stripe.api_key = settings.STRIPE_SECRET_KEY


class CreatePaymentIntentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        items = request.data.get('items', [])
        if not items:
            return Response({'detail': 'No items provided'}, status=400)

        total_cents = 0
        product_map = {}
        product_ids = [i['product_id'] for i in items]
        products = Product.objects.filter(id__in=product_ids, is_active=True)

        for product in products:
            product_map[product.id] = product
            total_cents += int(product.price * 100)

        if not product_map:
            return Response({'detail': 'No valid products found'}, status=400)

        order = Order.objects.create(user=request.user, total=total_cents / 100, status='pending')
        for item_data in items:
            product = product_map.get(item_data['product_id'])
            if product:
                OrderItem.objects.create(order=order, product=product, quantity=item_data.get('quantity', 1), price=product.price)

        intent = stripe.PaymentIntent.create(
            amount=total_cents, currency='usd',
            metadata={'order_id': str(order.id), 'user_id': str(request.user.id)}
        )

        order.payment_intent_id = intent['id']
        order.save()

        return Response({
            'client_secret': intent['client_secret'],
            'payment_intent_id': intent['id'],
            'amount': total_cents,
            'currency': 'usd',
        })


class ConfirmPaymentView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        payment_intent_id = request.data.get('payment_intent_id')
        try:
            order = Order.objects.get(payment_intent_id=payment_intent_id, user=request.user)
            intent = stripe.PaymentIntent.retrieve(payment_intent_id)
            if intent['status'] == 'succeeded':
                order.status = 'paid'
                order.save()
                for item in order.items.all():
                    item.product.sales_count += 1
                    item.product.save()
            return Response({'order_id': order.id, 'status': order.status})
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found'}, status=404)


@method_decorator(csrf_exempt, name='dispatch')
class StripeWebhookView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        payload = request.body
        sig_header = request.META.get('HTTP_STRIPE_SIGNATURE')

        try:
            event = stripe.Webhook.construct_event(payload, sig_header, settings.STRIPE_WEBHOOK_SECRET)
        except (ValueError, stripe.error.SignatureVerificationError):
            return Response({'detail': 'Invalid signature'}, status=400)

        if event['type'] == 'payment_intent.succeeded':
            intent = event['data']['object']
            order_id = intent['metadata'].get('order_id')
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'paid'
                order.save()
                for item in order.items.all():
                    item.product.sales_count += 1
                    item.product.save()
            except Order.DoesNotExist:
                pass

        elif event['type'] == 'payment_intent.payment_failed':
            intent = event['data']['object']
            order_id = intent['metadata'].get('order_id')
            try:
                order = Order.objects.get(id=order_id)
                order.status = 'failed'
                order.save()
            except Order.DoesNotExist:
                pass

        return Response({'status': 'ok'})
