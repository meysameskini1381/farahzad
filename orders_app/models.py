from django.db import models
from django.conf import settings
from products_app.models import Product


class Coupon(models.Model):
    DISCOUNT_TYPE_CHOICES = (
        ("percent", "Percent"),
        ("amount", "Amount"),
    )

    code = models.CharField(max_length=50, unique=True)

    discount_type = models.CharField(
        max_length=10,
        choices=DISCOUNT_TYPE_CHOICES
    )

    value = models.PositiveIntegerField()

    max_discount_amount = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    min_order_amount = models.PositiveIntegerField(default=0)

    is_active = models.BooleanField(default=True)

    usage_limit = models.PositiveIntegerField(
        null=True,
        blank=True
    )

    used_count = models.PositiveIntegerField(default=0)

    valid_from = models.DateTimeField()
    valid_to = models.DateTimeField()

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return self.code


class Order(models.Model):
    STATUS_CHOICES = (
        ("pending", "Pending Payment"),
        ("paid", "Paid"),
        ("failed", "Failed"),
        ("cancelled", "Cancelled"),
    )

    user = models.ForeignKey(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="orders"
    )

    address = models.ForeignKey(
        "accounts.UserAddress",
        on_delete=models.PROTECT,
        related_name="orders"
    )

    status = models.CharField(
        max_length=20,
        choices=STATUS_CHOICES,
        default="pending"
    )

    total_price = models.PositiveIntegerField()
    discount_amount = models.PositiveIntegerField(default=0)
    final_price = models.PositiveIntegerField()

    coupon = models.ForeignKey(
        Coupon,
        on_delete=models.SET_NULL,
        null=True,
        blank=True
    )

    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Order #{self.id}"

class OrderItem(models.Model):
    order = models.ForeignKey(
        Order,
        related_name="items",
        on_delete=models.CASCADE
    )

    product = models.ForeignKey(
        "product_app.Product",
        on_delete=models.PROTECT
    )

    quantity = models.PositiveIntegerField()
    price = models.PositiveIntegerField()

    def __str__(self):
        return f"Order {self.order_id} - {self.product_id}"

    @property
    def total_price(self):
        return self.price * self.quantity
