"""
ORDERS/MODELS.PY
Cart: temporary storage before purchase.
Order: permanent record of a completed (or attempted) purchase.
Once an Order is 'paid', the user can download via a signed, expiring URL.
"""
from django.db import models
from apps.users.models import User
from apps.products.models import Product


class CartItem(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='cart_items')
    product = models.ForeignKey(Product, on_delete=models.CASCADE)
    quantity = models.PositiveIntegerField(default=1)
    added_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = ['user', 'product']

    def __str__(self):
        return f'{self.user.email} — {self.product.title}'


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'Pending'), ('paid', 'Paid'),
        ('failed', 'Failed'), ('refunded', 'Refunded'),
    ]

    user = models.ForeignKey(User, on_delete=models.CASCADE, related_name='orders')
    status = models.CharField(max_length=20, choices=STATUS_CHOICES, default='pending')
    total = models.DecimalField(max_digits=10, decimal_places=2)
    payment_intent_id = models.CharField(max_length=200, unique=True, null=True, blank=True)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return f'Order #{self.id} — {self.user.email} — {self.status}'

    class Meta:
        ordering = ['-created_at']


class OrderItem(models.Model):
    order = models.ForeignKey(Order, on_delete=models.CASCADE, related_name='items')
    product = models.ForeignKey(Product, on_delete=models.PROTECT)
    quantity = models.PositiveIntegerField(default=1)
    price = models.DecimalField(max_digits=10, decimal_places=2)

    def __str__(self):
        return f'{self.product.title} x{self.quantity}'
