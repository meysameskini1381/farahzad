from rest_framework import serializers
from cart_app.models import Cart,CartItem

class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="product.title",
        read_only=True
    )

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_title",
            "quantity",
            "price",
            "total_price",
        ]

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "total_price",
            "items",
        ]