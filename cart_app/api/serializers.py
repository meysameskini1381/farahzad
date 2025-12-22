from rest_framework import serializers
from cart_app.models import Cart,CartItem


class CartItemSerializer(serializers.ModelSerializer):
    product_title = serializers.CharField(
        source="product.title",
        read_only=True
    )
    product_price = serializers.IntegerField(
        source="product.price",
        read_only=True
    )
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_title",
            "product_price",
            "quantity",
            "price",
            "total_price",
        ]
        read_only_fields = ["price"]  # قیمت snapshot فقط خواندنی باشد

class CartSerializer(serializers.ModelSerializer):
    items = CartItemSerializer(many=True, read_only=True)
    total_price = serializers.IntegerField(read_only=True)

    class Meta:
        model = Cart
        fields = [
            "id",
            "total_price",
            "items",
        ]
