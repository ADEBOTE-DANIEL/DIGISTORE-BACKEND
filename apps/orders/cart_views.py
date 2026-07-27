from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework import status
from apps.products.models import Product
from .models import CartItem
from .serializers import CartItemSerializer


class CartView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        items = CartItem.objects.filter(user=request.user).select_related('product')
        return Response(CartItemSerializer(items, many=True).data)


class CartAddView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        product_id = request.data.get('product_id')
        try:
            product = Product.objects.get(id=product_id, is_active=True)
        except Product.DoesNotExist:
            return Response({'detail': 'Product not found'}, status=404)

        item, created = CartItem.objects.get_or_create(user=request.user, product=product, defaults={'quantity': 1})
        if not created:
            return Response({'detail': 'Already in cart'}, status=400)
        return Response(CartItemSerializer(item).data, status=201)


class CartRemoveView(APIView):
    permission_classes = [IsAuthenticated]

    def delete(self, request, pk):
        CartItem.objects.filter(id=pk, user=request.user).delete()
        return Response(status=status.HTTP_204_NO_CONTENT)


class CartClearView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        CartItem.objects.filter(user=request.user).delete()
        return Response({'detail': 'Cart cleared'})
