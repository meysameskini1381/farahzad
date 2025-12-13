from django.db import models
from django.utils.text import slugify
from django_ckeditor_5.fields import CKEditor5Field

class Category(models.Model):
    title = models.CharField(
        max_length=200,
        verbose_name="عنوان دسته‌بندی",
        help_text="نام دسته‌بندی، مثل: میوه، سبزیجات، ترشیجات"
    )

    slug = models.SlugField(
        max_length=200,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
        help_text="آدرس URL دسته‌بندی، به صورت خودکار از عنوان ساخته می‌شود"
    )

    parent = models.ForeignKey(
        'self',
        on_delete=models.CASCADE,
        related_name='children',
        null=True,
        blank=True,
        verbose_name="دسته‌بندی والد",
        help_text="اگر این دسته‌بندی زیرمجموعه است، دسته‌بندی والد را انتخاب کنید"
    )

    is_main = models.BooleanField(
        default=False,
        verbose_name="دسته‌بندی اصلی",
        help_text="اگر این گزینه فعال باشد، این دسته‌بندی به عنوان دسته اصلی در نظر گرفته می‌شود"
    )

    image = models.ImageField(
        upload_to='categories/',
        null=True,
        blank=True,
        verbose_name="تصویر دسته‌بندی",
        help_text="تصویر نمایشی دسته‌بندی (برای صفحه دسته یا منو)"
    )

    meta_title = models.CharField(
        max_length=255,
        verbose_name="Meta Title",
        help_text="عنوان سئویی صفحه دسته‌بندی (حداکثر 60 کاراکتر)"
    )

    meta_description = models.TextField(
        verbose_name="Meta Description",
        help_text="توضیحات سئویی صفحه دسته‌بندی (حداکثر 160 کاراکتر)"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت فعال",
        help_text="اگر غیرفعال باشد، دسته‌بندی نمایش داده نمی‌شود"
    )

    ordering = models.PositiveIntegerField(
        default=0,
        verbose_name="ترتیب نمایش",
        help_text="عدد کمتر یعنی نمایش در جایگاه بالاتر"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
        help_text="تاریخ ایجاد دسته‌بندی"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
        help_text="آخرین زمان بروزرسانی"
    )

    class Meta:
        verbose_name = "دسته‌بندی"
        verbose_name_plural = "دسته‌بندی‌ها"
        ordering = ['ordering', 'title']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)




class Product(models.Model):
    category = models.ForeignKey(
        Category,
        on_delete=models.CASCADE,
        related_name='products',
        verbose_name="دسته‌بندی",
        help_text="دسته‌بندی‌ای که این محصول در آن قرار دارد"
    )

    title = models.CharField(
        max_length=250,
        verbose_name="نام محصول",
        help_text="نام محصول، مثل: سیب زرد ارگانیک"
    )

    slug = models.SlugField(
        max_length=250,
        unique=True,
        allow_unicode=True,
        verbose_name="اسلاگ",
        help_text="آدرس URL محصول، به صورت خودکار ساخته می‌شود"
    )

    description = CKEditor5Field(
        verbose_name="توضیحات کامل محصول",
        help_text="توضیحات کامل محصول، امکان درج تصویر، لینک nofollow و محتوای حرفه‌ای سئویی",
        config_name="default"
    )

    short_description = models.CharField(
        max_length=300,
        verbose_name="توضیح کوتاه",
        help_text="خلاصه توضیح محصول (برای لیست محصولات)"
    )

    image = models.ImageField(
        upload_to='products/',
        verbose_name="تصویر اصلی محصول",
        help_text="تصویر اصلی محصول که در صفحه محصول نمایش داده می‌شود"
    )

    price = models.PositiveIntegerField(
        verbose_name="قیمت",
        help_text="قیمت محصول به تومان"
    )

    discount_price = models.PositiveIntegerField(
        null=True,
        blank=True,
        verbose_name="قیمت با تخفیف",
        help_text="در صورت وجود تخفیف، قیمت نهایی محصول"
    )

    stock = models.PositiveIntegerField(
        verbose_name="موجودی",
        help_text="تعداد موجودی محصول در انبار"
    )

    is_available = models.BooleanField(
        default=True,
        verbose_name="موجود / ناموجود",
        help_text="اگر محصول موجود نیست غیرفعال شود"
    )

    meta_title = models.CharField(
        max_length=255,
        verbose_name="Meta Title",
        help_text="عنوان سئویی صفحه محصول (حداکثر 60 کاراکتر)"
    )

    meta_description = models.TextField(
        verbose_name="Meta Description",
        help_text="توضیحات سئویی صفحه محصول (حداکثر 160 کاراکتر)"
    )

    is_active = models.BooleanField(
        default=True,
        verbose_name="وضعیت فعال",
        help_text="اگر غیرفعال باشد، محصول در سایت نمایش داده نمی‌شود"
    )

    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name="تاریخ ایجاد",
        help_text="تاریخ ایجاد محصول"
    )

    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name="تاریخ بروزرسانی",
        help_text="آخرین زمان بروزرسانی محصول"
    )

    class Meta:
        verbose_name = "محصول"
        verbose_name_plural = "محصولات"
        ordering = ['-created_at']

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        if not self.slug:
            self.slug = slugify(self.title, allow_unicode=True)
        super().save(*args, **kwargs)