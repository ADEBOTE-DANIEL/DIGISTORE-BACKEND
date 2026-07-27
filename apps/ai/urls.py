from django.urls import path
from .views import AIChatView, AIRecommendView, AISearchView

urlpatterns = [
    path('chat/', AIChatView.as_view(), name='ai-chat'),
    path('recommend/', AIRecommendView.as_view(), name='ai-recommend'),
    path('search/', AISearchView.as_view(), name='ai-search'),
]
