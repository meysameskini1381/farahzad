from rest_framework.viewsets import ModelViewSet
from rest_framework.views import APIView
from rest_framework import status
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListAPIView
from products_app.models import Product
from .serializers import *
from products_app.models import Product,Category
from rest_framework.generics import RetrieveAPIView
from rest_framework.response import Response
from rest_framework.permissions import AllowAny
from django.http import JsonResponse
from rest_framework.decorators import api_view
from django.db.models import Q


def get_categories_api(request):
    """API endpoint برای دریافت دسته‌بندی‌های اصلی با فرزندان"""
    categories = Category.objects.filter(
        is_main=True,
        is_active=True
    ).prefetch_related(
        'children'  # ← این مهمه
    ).order_by('ordering', 'title')

    serializer = CategorySerializer(categories, many=True)

    return JsonResponse({
        'status': 'success',
        'data': serializer.data
    }, json_dumps_params={'ensure_ascii': False})  # ← برای فارسی

class ProductListAPIView(ListAPIView):
    queryset = Product.objects.filter(is_active=True)
    serializer_class = ProductSerializer

class ProductCategoryAPIView(ListAPIView):
    serializer_class = ProductSerializer
    pagination_class = ProductPagination

    def get_queryset(self):
        qs = Product.objects.filter(is_active=True)

        # category
        category_slug = self.request.GET.get("category")
        if category_slug:
            qs = qs.filter(category__slug=category_slug)

        # price filter
        min_price = self.request.GET.get("min_price")
        max_price = self.request.GET.get("max_price")

        if min_price:
            qs = qs.filter(price__gte=min_price)
        if max_price:
            qs = qs.filter(price__lte=max_price)

        # VIP
        vip = self.request.GET.get("vip")
        if vip == "1":
            qs = qs.filter(vip=True)

        # ordering
        ordering = self.request.GET.get("ordering")
        if ordering:
            qs = qs.order_by(ordering)

        return qs

class ProductDetailAPIView(RetrieveAPIView):
    serializer_class = ProductDetailSerializer
    lookup_field = 'slug'

    def get_queryset(self):
        return Product.objects.filter(is_active=True)


class ProductCommentBySlugAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request, slug):
        product = get_object_or_404(Product, slug=slug)

        serializer = ProductCommentCreateSerializer(
            data=request.data,
            context={
                'request': request,
                'product': product
            }
        )
        serializer.is_valid(raise_exception=True)
        serializer.save()

        return Response(serializer.data, status=status.HTTP_201_CREATED)


def search_products(request):
    query = request.GET.get('q', '').strip()

    if len(query) < 2:
        return JsonResponse({
            'results': [],
            'message': 'حداقل 2 کاراکتر وارد کنید'
        })

    products = Product.objects.filter(
        Q(title__icontains=query) |
        Q(short_description__icontains=query) |
        Q(category__title__icontains=query),
        is_active=True
    ).select_related('category').distinct()[:10]

    serializer = ProductSearchSerializer(products, many=True, context={'request': request})

    return JsonResponse({
        'results': serializer.data,
        'count': len(serializer.data)
    })