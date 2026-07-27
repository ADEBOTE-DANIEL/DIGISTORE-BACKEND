from django.urls import path
from .cart_views import CartView, CartAddView, CartRemoveView, CartClearView

urlpatterns = [
    path('', CartView.as_view(), name='cart'),
    path('add/', CartAddView.as_view(), name='cart-add'),
    path('remove/<int:pk>/', CartRemoveView.as_view(), name='cart-remove'),
    path('clear/', CartClearView.as_view(), name='cart-clear'),
]
