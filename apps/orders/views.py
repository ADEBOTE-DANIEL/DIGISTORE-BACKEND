"""
ORDERS/VIEWS.PY
HOW SECURE DOWNLOADS WORK:
  1. Check the user owns this order and it's paid
  2. Generate a signed, time-limited download URL (expires in 1 hour)
  3. Return the URL to the app
  Signature uses HMAC-SHA256 with the Django SECRET_KEY so it can't be forged.
"""
import hmac
import hashlib
import time
from django.conf import settings
from rest_framework import generics
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .models import Order
from .serializers import OrderSerializer


class MyOrdersView(generics.ListAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items__product')


class OrderDetailView(generics.RetrieveAPIView):
    serializer_class = OrderSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user)


class DownloadView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, pk):
        try:
            order = Order.objects.get(id=pk, user=request.user, status='paid')
        except Order.DoesNotExist:
            return Response({'detail': 'Order not found or not paid'}, status=404)

        expires_at = int(time.time()) + 3600
        message = f'{order.id}:{expires_at}'
        signature = hmac.new(settings.SECRET_KEY.encode(), message.encode(), hashlib.sha256).hexdigest()
        download_url = f'{request.build_absolute_uri("/api/orders/")}{order.id}/file/?token={signature}&expires={expires_at}'

        return Response({'url': download_url, 'expires': expires_at})
