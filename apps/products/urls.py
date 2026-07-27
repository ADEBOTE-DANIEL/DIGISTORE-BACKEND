from django.urls import path
from .views import ProductListView, ProductDetailView, FeaturedProductsView, CategoryListView, SearchView

urlpatterns = [
    path('', ProductListView.as_view(), name='product-list'),
    path('<int:pk>/', ProductDetailView.as_view(), name='product-detail'),
    path('featured/', FeaturedProductsView.as_view(), name='featured'),
    path('categories/', CategoryListView.as_view(), name='categories'),
    path('search/', SearchView.as_view(), name='search'),
]
