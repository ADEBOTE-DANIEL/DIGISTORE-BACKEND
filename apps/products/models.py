from django.db import models

class Category(models.Model):
    name = models.CharField(max_length=100)
    slug = models.SlugField(unique=True)
    icon = models.CharField(max_length=10, default='📁')

    def __str__(self):
        return self.name

    class Meta:
        verbose_name_plural = 'categories'


class Product(models.Model):
    title = models.CharField(max_length=255)
    description = models.TextField()
    price = models.DecimalField(max_digits=10, decimal_places=2)
    category = models.ForeignKey(Category, on_delete=models.SET_NULL, null=True, related_name='products')

    digital_file = models.FileField(upload_to='products/files/', null=True, blank=True)
    preview_url = models.URLField(null=True, blank=True)
    file_size = models.CharField(max_length=50, default='Unknown')
    file_type = models.CharField(max_length=50, default='ZIP')

    thumbnail = models.URLField(max_length=500)
    is_featured = models.BooleanField(default=False)
    is_active = models.BooleanField(default=True)

    rating = models.DecimalField(max_digits=3, decimal_places=2, default=0.0)
    review_count = models.PositiveIntegerField(default=0)
    sales_count = models.PositiveIntegerField(default=0)

    tags = models.JSONField(default=list)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self):
        return self.title

    class Meta:
        ordering = ['-created_at']
