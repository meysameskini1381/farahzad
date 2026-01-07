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
    product_discount_price = serializers.SerializerMethodField()
    product_image = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    has_discount = serializers.SerializerMethodField()
    discount_percent = serializers.SerializerMethodField()
    final_price = serializers.SerializerMethodField()

    class Meta:
        model = CartItem
        fields = [
            "id",
            "product",
            "product_title",
            "product_price",
            "product_discount_price",
            "product_image",
            "quantity",
            "price",
            "total_price",
            "has_discount",
            "discount_percent",
            "final_price",
        ]
        read_only_fields = ["price"]

    def get_product_image(self, obj):
        """برگردوندن URL کامل عکس محصول"""
        try:
            if obj.product.image:
                request = self.context.get('request')
                if request:
                    return request.build_absolute_uri(obj.product.image.url)
                return obj.product.image.url
            return None
        except Exception as e:
            print(f"Error getting image: {e}")
            return None

    def get_product_discount_price(self, obj):
        """برگردوندن قیمت تخفیف‌خورده"""
        try:
            if hasattr(obj.product, 'discount_price') and obj.product.discount_price:
                return int(obj.product.discount_price)
            return None
        except Exception:
            return None

    def get_has_discount(self, obj):
        """بررسی اینکه محصول تخفیف داره یا نه"""
        try:
            discount_price = self.get_product_discount_price(obj)
            if discount_price and discount_price < obj.product.price:
                return True
            return False
        except Exception:
            return False

    def get_discount_percent(self, obj):
        """محاسبه درصد تخفیف"""
        try:
            if not self.get_has_discount(obj):
                return 0

            discount_price = self.get_product_discount_price(obj)
            original_price = obj.product.price

            percent = ((original_price - discount_price) / original_price) * 100
            return round(percent)
        except Exception:
            return 0

    def get_final_price(self, obj):
        """قیمت نهایی (با احتساب تخفیف)"""
        discount_price = self.get_product_discount_price(obj)
        if discount_price and discount_price < obj.product.price:
            return discount_price
        return obj.product.price

    def get_total_price(self, obj):
        """محاسبه قیمت کل = قیمت نهایی × تعداد"""
        final_price = self.get_final_price(obj)
        return final_price * obj.quantity


class CartSerializer(serializers.ModelSerializer):
    items = serializers.SerializerMethodField()
    total_price = serializers.SerializerMethodField()
    total_discount = serializers.SerializerMethodField()
    original_total = serializers.SerializerMethodField()

    class Meta:
        model = Cart
        fields = [
            "id",
            "total_price",
            "total_discount",
            "original_total",
            "items",
        ]

    def get_items(self, obj):
        """برگردوندن آیتم‌ها با ترتیب ثابت"""
        items = obj.items.select_related('product').order_by('id')
        return CartItemSerializer(items, many=True, context=self.context).data

    def get_original_total(self, obj):
        """مجموع قیمت اصلی (بدون تخفیف)"""
        total = 0
        for item in obj.items.all():
            total += item.product.price * item.quantity
        return total

    def get_total_price(self, obj):
        """مجموع قیمت نهایی (با احتساب تخفیف)"""
        total = 0
        for item in obj.items.all():
            # استفاده از قیمت تخفیف‌خورده اگه داشت
            if hasattr(item.product, 'discount_price') and item.product.discount_price:
                if item.product.discount_price < item.product.price:
                    total += item.product.discount_price * item.quantity
                else:
                    total += item.product.price * item.quantity
            else:
                total += item.product.price * item.quantity
        return total

    def get_total_discount(self, obj):
        """مجموع تخفیف کل سبد"""
        original = self.get_original_total(obj)
        final = self.get_total_price(obj)
        return original - final