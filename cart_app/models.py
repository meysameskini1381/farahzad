from django.conf import settings
from django.db import models
from products_app.models import Product

class Cart(models.Model):
    user = models.OneToOneField(
        settings.AUTH_USER_MODEL,
        on_delete=models.CASCADE,
        related_name="cart",
        verbose_name="کاربر"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="آخرین بروزرسانی"
    )

    class Meta:
        verbose_name = "سبد خرید"
        verbose_name_plural = "سبدهای خرید"

    def __str__(self):
        return f"Cart of {self.user}"

    @property
    def total_price(self):
        return sum(item.total_price for item in self.items.all())


class CartItem(models.Model):
    cart = models.ForeignKey(
        Cart,
        related_name="items",
        on_delete=models.CASCADE,
        verbose_name="سبد خرید"
    )

    product = models.ForeignKey(
        Product,
        on_delete=models.CASCADE,
        verbose_name="محصول"
    )

    quantity = models.PositiveIntegerField(
        default=1,
        verbose_name="تعداد"
    )

    price = models.PositiveIntegerField(
        verbose_name="قیمت واحد (snapshot)"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="زمان اضافه شدن"
    )

    class Meta:
        verbose_name = "آیتم سبد خرید"
        verbose_name_plural = "آیتم‌های سبد خرید"
        unique_together = ("cart", "product")

    def __str__(self):
        return f"{self.product.title} × {self.quantity}"

    @property
    def total_price(self):
        return self.price * self.quantity
