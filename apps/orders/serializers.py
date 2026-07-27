from rest_framework import serializers
from apps.products.serializers import ProductSerializer
from .models import CartItem, Order, OrderItem


class CartItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)
    product_id = serializers.IntegerField(write_only=True)

    class Meta:
        model = CartItem
        fields = ['id', 'product', 'product_id', 'quantity', 'added_at']
        read_only_fields = ['id', 'added_at']


class OrderItemSerializer(serializers.ModelSerializer):
    product = ProductSerializer(read_only=True)

    class Meta:
        model = OrderItem
        fields = ['id', 'product', 'quantity', 'price']


class OrderSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)

    class Meta:
        model = Order
        fields = ['id', 'items', 'total', 'status', 'payment_intent_id', 'created_at']
        read_only_fields = ['id', 'total', 'status', 'created_at']
