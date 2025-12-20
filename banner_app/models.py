from django.db import models

class Banner(models.Model):
    BANNER_POSITIONS = (
        ("بنر اصلی", "بنر اصلی"),
        ("بنر محصولات vip", "بنر محصولات vip"),
        ("بنر جدید ترین ها", "بنر جدید ترین ها"),
        ("بنر تخفیف", "بنر تخفیف"),
    )

    title = models.CharField(max_length=255,verbose_name="اسم بنر مورد نظر شما ؟ ",unique=True)
    image = models.ImageField(upload_to="banners/", verbose_name='اپلود تصویر')
    link = models.URLField(blank=True,verbose_name='لینک بنر را وارد کنید')

    position = models.CharField(
        max_length=50,
        choices=BANNER_POSITIONS,
        db_index=True,
        verbose_name='جایگاه'
    )

    is_active = models.BooleanField(default=True,verbose_name='فعال/غیر فعال')

    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        verbose_name = "بنر"
        verbose_name_plural = "بنر سایت "
        ordering = ['-created_at']

    def __str__(self):
        return f"{self.title} ({self.position})"