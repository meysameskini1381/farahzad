# orders_app/api/serializers.py

from rest_framework import serializers
from orders_app.models import Order, OrderItem, Coupon, CouponUsage
from accounts_app.models import Address
from cart_app.models import Cart


class OrderItemSerializer(serializers.ModelSerializer):
    class Meta:
        model = OrderItem
        fields = [
            'id',
            'product',
            'product_name',
            'product_image',
            'quantity',
            'price',
            'total_price'
        ]
        read_only_fields = fields


class OrderListSerializer(serializers.ModelSerializer):
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'status_display',
            'total_amount',
            'items_count',
            'created_at'
        ]
        read_only_fields = fields


class OrderDetailSerializer(serializers.ModelSerializer):
    items = OrderItemSerializer(many=True, read_only=True)
    status_display = serializers.CharField(source='get_status_display', read_only=True)

    class Meta:
        model = Order
        fields = [
            'id',
            'order_number',
            'status',
            'status_display',
            'address_snapshot',
            'coupon_code',
            'subtotal',
            'discount_amount',
            'shipping_cost',
            'total_amount',
            'items',
            'notes',
            'created_at',
            'updated_at',
            'paid_at'
        ]
        read_only_fields = fields


class CouponValidationSerializer(serializers.Serializer):
    code = serializers.CharField(max_length=50)

    def validate_code(self, value):
        try:
            coupon = Coupon.objects.get(code=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("کوپن تخفیف معتبر نیست")

        if not coupon.is_valid():
            raise serializers.ValidationError("کوپن تخفیف منقضی شده است")

        user = self.context['request'].user
        if not coupon.can_user_use(user):
            raise serializers.ValidationError("شما قبلاً از این کوپن استفاده کرده‌اید")

        try:
            cart = Cart.objects.get(user=user)
            cart_total = cart.total_price
        except Cart.DoesNotExist:
            raise serializers.ValidationError("سبد خرید خالی است")

        if not coupon.can_use_for_amount(cart_total):
            raise serializers.ValidationError(
                f"حداقل مبلغ خرید برای این کوپن {coupon.min_purchase_amount:,} تومان است"
            )

        return value


class CheckoutSerializer(serializers.Serializer):
    address_id = serializers.IntegerField()
    coupon_code = serializers.CharField(max_length=50, required=False, allow_blank=True)
    notes = serializers.CharField(required=False, allow_blank=True)

    def validate_address_id(self, value):
        user = self.context['request'].user

        try:
            address = Address.objects.get(id=value, profile=user.profile)
            return address
        except Address.DoesNotExist:
            raise serializers.ValidationError("آدرس انتخابی یافت نشد")

    def validate_coupon_code(self, value):
        if not value:
            return None

        try:
            coupon = Coupon.objects.get(code=value)
        except Coupon.DoesNotExist:
            raise serializers.ValidationError("کوپن تخفیف معتبر نیست")

        if not coupon.is_valid():
            raise serializers.ValidationError("کوپن تخفیف منقضی شده است")

        user = self.context['request'].user
        if not coupon.can_user_use(user):
            raise serializers.ValidationError("شما قبلاً از این کوپن استفاده کرده‌اید")

        try:
            cart = Cart.objects.get(user=user)
            cart_total = cart.total_price
        except Cart.DoesNotExist:
            raise serializers.ValidationError("سبد خرید خالی است")

        if not coupon.can_use_for_amount(cart_total):
            raise serializers.ValidationError(
                f"حداقل مبلغ خرید برای این کوپن {coupon.min_purchase_amount:,} تومان است"
            )

        return coupon

    def create(self, validated_data):
        user = self.context['request'].user

        # اینجا address_id دیگه یه آبجکت Address هست چون از validate_address_id برگشته
        address = validated_data['address_id']

        # coupon_code هم الان یه آبجکت Coupon هست یا None
        coupon = validated_data.get('coupon_code')
        notes = validated_data.get('notes', '')

        # ایجاد سفارش
        order = Order.create_from_cart(
            user=user,
            address=address,
            coupon=coupon,
            notes=notes
        )

        return order
