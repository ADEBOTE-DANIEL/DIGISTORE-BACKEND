from django.urls import path
from .views import MyOrdersView, OrderDetailView, DownloadView

urlpatterns = [
    path('my-orders/', MyOrdersView.as_view(), name='my-orders'),
    path('<int:pk>/', OrderDetailView.as_view(), name='order-detail'),
    path('<int:pk>/download/', DownloadView.as_view(), name='order-download'),
]
