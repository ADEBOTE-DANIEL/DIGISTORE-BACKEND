"""
AI/VIEWS.PY — Google Gemini AI Integration
============================================
All AI calls go through Django — the Gemini API key never touches
the React Native app. gemini-1.5-flash is fast and free-tier friendly.

Free tier (as of writing): 15 req/min, 1M tokens/min, 1,500 req/day.
"""

import json
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Product
from apps.products.serializers import ProductSerializer
from apps.orders.models import Order

import json
from groq import Groq
from django.conf import settings
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from apps.products.models import Product
from apps.products.serializers import ProductSerializer
from apps.orders.models import Order

client = Groq(api_key=settings.GROQ_API_KEY)


def get_product_context():
    products = Product.objects.filter(is_active=True).values(
        'id', 'title', 'price', 'category__name', 'tags', 'rating'
    )[:50]
    return json.dumps(list(products), default=str)

class AIChatView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        messages = request.data.get('messages', [])
        if not messages:
            return Response({'detail': 'No messages provided'}, status=400)

        product_context = get_product_context()

        system_prompt = f"""You are DigiStore's helpful AI assistant. You help customers
find the perfect digital products and answer questions about orders, downloads, and the store.

Here are our current products (JSON):
{product_context}

Be friendly, concise, and helpful. Keep responses under 200 words."""

        groq_messages = [{"role": "system", "content": system_prompt}]
        for msg in messages[-10:]:
            groq_messages.append({"role": msg['role'], "content": msg['content']})

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=groq_messages,
                max_tokens=500
            )
            reply = response.choices[0].message.content.strip()
            return Response({'message': reply, 'suggestions': []})
        except Exception as e:
            return Response({'detail': f'AI error: {str(e)}'}, status=500)

class AIRecommendView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        viewed_ids = request.data.get('viewed_products', [])
        purchased_ids = list(Order.objects.filter(user=request.user, status='paid').values_list('items__product_id', flat=True))

        all_products = Product.objects.filter(is_active=True).exclude(id__in=purchased_ids).values(
            'id', 'title', 'price', 'category__name', 'tags', 'rating'
        )
        viewed_titles = list(Product.objects.filter(id__in=viewed_ids).values_list('title', flat=True))

        prompt = f"""You are a recommendation engine for DigiStore.

Available products: {json.dumps(list(all_products), default=str)}
Products the user viewed: {viewed_titles}

Return ONLY a JSON array of 4 product IDs like [1, 2, 3, 4]. No other text."""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            text = response.choices[0].message.content.strip()
            text = text.replace('```json', '').replace('```', '').strip()
            product_ids = json.loads(text)
            products = Product.objects.filter(id__in=product_ids, is_active=True)
            return Response({'products': ProductSerializer(products, many=True).data, 'reason': 'Recommended for you'})
        except Exception:
            products = Product.objects.filter(is_active=True, is_featured=True)[:4]
            return Response({'products': ProductSerializer(products, many=True).data, 'reason': 'Top picks'})

class AISearchView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        query = request.data.get('query', '').strip()
        if not query:
            return Response([], status=200)

        product_context = get_product_context()

        prompt = f"""You are a search engine for DigiStore.

User query: "{query}"
Available products: {product_context}

Return ONLY a JSON array of matching product IDs like [1, 5, 12]. No other text."""

        try:
            response = client.chat.completions.create(
                model="llama-3.3-70b-versatile",
                messages=[{"role": "user", "content": prompt}],
                max_tokens=100
            )
            text = response.choices[0].message.content.strip()
            text = text.replace('```json', '').replace('```', '').strip()
            product_ids = json.loads(text)
            products = Product.objects.filter(id__in=product_ids, is_active=True)
            return Response(ProductSerializer(products, many=True).data)
        except Exception:
            products = Product.objects.filter(is_active=True, title__icontains=query)[:8]
            return Response(ProductSerializer(products, many=True).data)
