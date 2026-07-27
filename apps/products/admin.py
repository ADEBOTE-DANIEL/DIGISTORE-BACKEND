from django.contrib import admin
from .models import Product, Category

@admin.register(Category)
class CategoryAdmin(admin.ModelAdmin):
    list_display = ['name', 'slug', 'icon']
    prepopulated_fields = {'slug': ('name',)}

@admin.register(Product)
class ProductAdmin(admin.ModelAdmin):
    list_display = ['title', 'price', 'category', 'is_featured', 'is_active', 'sales_count', 'created_at']
    list_filter = ['category', 'is_featured', 'is_active']
    search_fields = ['title', 'description']
    list_editable = ['is_featured', 'is_active']
