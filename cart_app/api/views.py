from rest_framework.views import APIView
from rest_framework.permissions import IsAuthenticated
from rest_framework.response import Response
from rest_framework import status
from django.shortcuts import get_object_or_404
from cart_app.models import Cart, CartItem
from products_app.models import Product
from cart_app.api.serializers import CartSerializer


class AddToCartAPIView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        product_id = request.data.get("product_id")
        quantity = request.data.get("quantity", 1)

        # اعتبارسنجی ابتدایی
        if not product_id:
            return Response(
                {"detail": "product_id is required"},
                status=status.HTTP_400_BAD_REQUEST
            )

        try:
            quantity = int(quantity)
            if quantity <= 0:
                raise ValueError
        except ValueError:
            return Response(
                {"detail": "quantity must be a positive integer"},
                status=status.HTTP_400_BAD_REQUEST
            )

        # محصول
        product = get_object_or_404(
            Product,
            id=product_id,
            is_active=True
        )

        # cart کاربر (اگر نبود ساخته می‌شود)
        cart, _ = Cart.objects.get_or_create(user=user)

        # cart item
        item, created = CartItem.objects.get_or_create(
            cart=cart,
            product=product,
            defaults={
                "quantity": quantity,
                "price": product.price,  # snapshot
            }
        )

        # اگر قبلاً داخل cart بوده → فقط quantity زیاد شود
        if not created:
            item.quantity += quantity
            item.save()

        # پاسخ
        serializer = CartSerializer(cart)
        return Response(serializer.data, status=status.HTTP_200_OK)

