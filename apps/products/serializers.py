from rest_framework import serializers
from .models import Product, Category

class CategorySerializer(serializers.ModelSerializer):
    class Meta:
        model = Category
        fields = ['id', 'name', 'icon', 'slug']

class ProductSerializer(serializers.ModelSerializer):
    category = CategorySerializer(read_only=True)

    class Meta:
        model = Product
        fields = [
            'id', 'title', 'description', 'price', 'category',
            'thumbnail', 'preview_url', 'file_size', 'file_type',
            'rating', 'review_count', 'is_featured', 'tags', 'created_at'
        ]
        # digital_file excluded — downloads only via signed URLs in orders app
