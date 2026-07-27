"""
ROOT URL CONFIGURATION
======================
When a request comes in, Django looks through urlpatterns in order
and routes to the first match. include() delegates matching URLs
to another urls.py file in that app.

Example: GET /api/products/ -> routed to apps/products/urls.py
"""

from django.contrib import admin
from django.urls import path, include
from django.conf import settings
from django.conf.urls.static import static

urlpatterns = [
    path('admin/', admin.site.urls),
    path('api/auth/', include('apps.users.urls')),
    path('api/products/', include('apps.products.urls')),
    path('api/orders/', include('apps.orders.urls')),
    path('api/payments/', include('apps.payments.urls')),
    path('api/cart/', include('apps.orders.cart_urls')),
    path('api/ai/', include('apps.ai.urls')),
]

if settings.DEBUG:
    urlpatterns += static(settings.MEDIA_URL, document_root=settings.MEDIA_ROOT)
