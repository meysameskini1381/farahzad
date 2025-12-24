# orders_app/models.py

from django.db import models
from django.conf import settings
from django.utils import timezone
from decimal import Decimal
import uuid
from accounts_app.models import Address
from products_app.models import Product
from cart_app.models import Cart


class Coupon(models.Model):
    code = models.CharField(
        max_length=50,
        unique=True,
        verbose_name="کد تخفیف"
    )

    discount_percentage = models.DecimalField(
        max_digits=5,
        decimal_places=2,
        default=0,
        verbose_name="درصد تخفیف"
    )

    discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="مبلغ ثابت تخفیف"
    )

    max_discount_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        null=True,
        blank=True,
        verbose_name="حداکثر مبلغ تخفیف"
    )

    min_purchase_amount = models.DecimalField(
        max_digits=10,
        decimal_places=2,
        default=0,
        verbose_name="حداقل مبلغ خرید"
    )

    usage_limit = models.IntegerField(
        default=1,
        verbose_name="تعداد کل استفاده"
    )

    used_count = models.IntegerField(
        default=0,
        verbose_name="تعداد استفاده شده"
    )

    per_user_limit = models.IntegerField(
        default=1,
        verbose_name="تعداد استفاده هر کاربر"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="فعال"
    )

    valid_from = models.DateTimeField(
        verbose_name="تاریخ شروع اعتبار"
    )

    valid_to = models.DateTimeField(
        verbose_name="تاریخ پایان اعتبار"
    )

    description = models.TextField(
        blank=True,
        verbose_name="توضیحات"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ ویرایش"
    )

    class Meta:
        verbose_name = "کوپن تخفیف"
        verbose_name_plural = "کوپن‌های تخفیف"
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.code} - {self.discount_percentage}%"

    def is_valid(self):
        now = timezone.now()
        return (
                self.is_active and
                self.valid_from <= now <= self.valid_to and
                self.used_count < self.usage_limit
        )

    def can_use_for_amount(self, amount):
        return Decimal(str(amount)) >= self.min_purchase_amount

    def user_usage_count(self, user):
        return CouponUsage.objects.filter(user=user, coupon=self).count()

    def can_user_use(self, user):
        return self.user_usage_count(user) < self.per_user_limit

    def calculate_discount(self, amount):
        amount = Decimal(str(amount))

        if self.discount_amount:
            discount = self.discount_amount
        else:
            discount = (amount * self.discount_percentage) / Decimal('100')

        if self.max_discount_amount:
            discount = min(discount, self.max_discount_amount)

        return discount


class Order(models.Model):
    STATUS_CHOICES = [
        ('pending', 'در انتظار پرداخت'),
        ('paid', 'پرداخت شده'),
        ('processing', 'در حال پردازش'),
        ('shipping', 'در حال ارسال'),
        ('delivered', 'تحویل داده شده'),
        ('cancelled', 'لغو شده'),
        ('returned', 'مرجوع شده'),
    ]

    order_number = models.CharField(
        max_length=50,
        unique=True,
        editable=False,
        verbose_name="شماره سفارش"
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='orders',
        verbose_name="کاربر"
    )

    address = models.ForeignKey(
        Address,
        on_delete=models.SET_NULL,
        null=True,
        related_name='orders',
        verbose_name="آدرس"
    )

    address_snapshot = models.JSONField(
        null=True,
        blank=True,
        verbose_name="اسنپ‌شات آدرس"
    )

    coupon = models.ForeignKey(
        'Coupon',
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name='orders',
        verbose_name="کوپن"
    )

    coupon_code = models.CharField(
        max_length=50,
        blank=True,
        verbose_name="کد تخفیف استفاده شده"
    )

    subtotal = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="جمع محصولات"
    )

    discount_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="مبلغ تخفیف"
    )

    shipping_cost = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        default=0,
        verbose_name="هزینه ارسال"
    )

    total_amount = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="مبلغ نهایی"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default='pending',
        verbose_name="وضعیت"
    )

    notes = models.TextField(
        blank=True,
        verbose_name="یادداشت مشتری"
    )

    admin_notes = models.TextField(
        blank=True,
        verbose_name="یادداشت ادمین"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ثبت سفارش"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ به‌روزرسانی"
    )

    paid_at = models.DateTimeField(
        null=True,
        blank=True,
        verbose_name="تاریخ پرداخت"
    )

    class Meta:
        verbose_name = "سفارش"
        verbose_name_plural = "سفارشات"
        ordering = ['-created_at']
        indexes = [
            models.Index(fields=['-created_at']),
            models.Index(fields=['order_number']),
            models.Index(fields=['user', '-created_at']),
        ]

    def __str__(self):
        return f"سفارش {self.order_number} - {self.user.phone}"

    def save(self, *args, **kwargs):
        if not self.order_number:
            self.order_number = self.generate_order_number()

        if self.address and not self.address_snapshot:
            self.address_snapshot = {
                'title': self.address.title,
                'full_address': self.address.full_address,
            }

        super().save(*args, **kwargs)

    def generate_order_number(self):
        timestamp = timezone.now().strftime('%y%m%d')
        unique_id = uuid.uuid4().hex[:6].upper()
        return f"ORD{timestamp}{unique_id}"

    def calculate_totals(self):
        self.subtotal = sum(
            Decimal(str(item.total_price))
            for item in self.items.all()
        )

        if self.coupon and self.coupon.is_valid():
            if self.coupon.can_use_for_amount(self.subtotal):
                self.discount_amount = self.coupon.calculate_discount(self.subtotal)
            else:
                self.discount_amount = Decimal('0')
        else:
            self.discount_amount = Decimal('0')

        self.total_amount = self.subtotal - self.discount_amount + self.shipping_cost
        self.save()

    @property
    def items_count(self):
        return sum(item.quantity for item in self.items.all())

    @classmethod
    def create_from_cart(cls, user, address, coupon=None, notes=''):
        try:
            cart = Cart.objects.get(user=user)
        except Cart.DoesNotExist:
            raise ValueError("سبد خرید خالی است")

        if not cart.items.exists():
            raise ValueError("سبد خرید خالی است")

        subtotal = Decimal('0')
        for cart_item in cart.items.all():
            item_price = cart_item.product.discount_price if cart_item.product.discount_price else cart_item.product.price
            subtotal += Decimal(str(item_price)) * cart_item.quantity

        discount_amount = Decimal('0')
        if coupon:
            if not coupon.is_valid():
                raise ValueError("کوپن نامعتبر است")
            if not coupon.can_use_for_amount(subtotal):
                raise ValueError(f"حداقل مبلغ خرید برای این کوپن {coupon.min_purchase_amount} تومان است")
            if not coupon.can_user_use(user):
                raise ValueError("شما قبلاً از این کوپن استفاده کرده‌اید")

            discount_amount = coupon.calculate_discount(subtotal)

        shipping_cost = Decimal('0')
        total_amount = subtotal - discount_amount + shipping_cost

        order = cls.objects.create(
            user=user,
            address=address,
            coupon=coupon,
            coupon_code=coupon.code if coupon else '',
            subtotal=subtotal,
            discount_amount=discount_amount,
            shipping_cost=shipping_cost,
            total_amount=total_amount,
            notes=notes,
            address_snapshot={
                'title': address.title,
                'full_address': address.full_address,
            }
        )

        for cart_item in cart.items.all():
            if cart_item.product.stock < cart_item.quantity:
                order.delete()
                raise ValueError(
                    f"موجودی محصول {cart_item.product.title} کافی نیست. "
                    f"موجودی فعلی: {cart_item.product.stock}"
                )

            item_price = cart_item.product.discount_price if cart_item.product.discount_price else cart_item.product.price

            OrderItem.objects.create(
                order=order,
                product=cart_item.product,
                product_name=cart_item.product.title,
                product_image=cart_item.product.image.name if cart_item.product.image else '',
                quantity=cart_item.quantity,
                price=Decimal(str(item_price))
            )

            cart_item.product.stock -= cart_item.quantity
            cart_item.product.save()

        if coupon:
            CouponUsage.objects.create(
                user=user,
                coupon=coupon,
                order=order
            )
            coupon.used_count += 1
            coupon.save()

        cart.items.all().delete()

        return order


class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='items',
        verbose_name="سفارش"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        related_name='order_items',
        verbose_name="محصول"
    )

    product_name = models.CharField(
        max_length=255,
        verbose_name="نام محصول"
    )

    product_image = models.CharField(
        max_length=500,
        blank=True,
        verbose_name="مسیر تصویر"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد"
    )

    price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="قیمت واحد"
    )

    total_price = models.DecimalField(
        max_digits=12,
        decimal_places=2,
        verbose_name="قیمت کل"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    class Meta:
        verbose_name = "قلم سفارش"
        verbose_name_plural = "اقلام سفارش"
        ordering = ['id']

    def __str__(self):
        return f"{self.product_name} × {self.quantity}"

    def save(self, *args, **kwargs):
        if not self.product_name:
            self.product_name = self.product.title

        if not self.product_image and self.product.image:
            self.product_image = self.product.image.name

        self.total_price = self.price * Decimal(str(self.quantity))

        super().save(*args, **kwargs)


class CouponUsage(models.Model):
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name="کاربر"
    )

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.CASCADE,
        related_name='usages',
        verbose_name="کوپن"
    )

    order = models.ForeignKey(
        Order,
        on_delete=models.CASCADE,
        related_name='coupon_usages',
        verbose_name="سفارش"
    )

    used_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ استفاده"
    )

    class Meta:
        verbose_name = "استفاده از کوپن"
        verbose_name_plural = "استفاده‌های کوپن"
        unique_together = ['user', 'coupon', 'order']
        ordering = ['-used_at']

    def __str__(self):
        return f"{self.user.phone} - {self.coupon.code} - {self.order.order_number}"
