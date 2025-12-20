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
