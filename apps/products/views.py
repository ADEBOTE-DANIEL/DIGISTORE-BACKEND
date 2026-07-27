from rest_framework import generics, filters
from rest_framework.permissions import AllowAny
from rest_framework.views import APIView
from rest_framework.response import Response
from .models import Product, Category
from .serializers import ProductSerializer, CategorySerializer


class ProductListView(generics.ListAPIView):
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]
    filter_backends = [filters.OrderingFilter]
    ordering_fields = ['price', 'rating', 'created_at', 'sales_count']
    ordering = ['-created_at']

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)
        category = self.request.query_params.get('category')
        if category:
            qs = qs.filter(category_id=category)
        return qs


class ProductDetailView(generics.RetrieveAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class FeaturedProductsView(generics.ListAPIView):
    queryset = Product.objects.filter(is_active=True, is_featured=True)[:10]
    serializer_class = ProductSerializer
    permission_classes = [AllowAny]


class CategoryListView(generics.ListAPIView):
    queryset = Category.objects.all()
    serializer_class = CategorySerializer
    permission_classes = [AllowAny]


class SearchView(APIView):
    permission_classes = [AllowAny]

    def get(self, request):
        query = request.query_params.get('q', '')
        if not query:
            return Response([])
        products = Product.objects.filter(is_active=True, title__icontains=query) | \
                   Product.objects.filter(is_active=True, description__icontains=query)
        return Response(ProductSerializer(products.distinct(), many=True).data)
