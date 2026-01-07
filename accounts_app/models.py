from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    PermissionsMixin,
    BaseUserManager
)
from django_ckeditor_5.fields import CKEditor5Field
from django.conf import settings
from django.db.models.signals import post_save
from django.dispatch import receiver
from django.utils import timezone
import random

class UserManager(BaseUserManager):
    def create_user(self, phone, password=None, **extra_fields):
        if not phone:
            raise ValueError("Phone number is required")

        user = self.model(
            phone=phone,
            **extra_fields
        )

        if password:
            user.set_password(password)
        else:
            user.set_unusable_password()

        user.save(using=self._db)
        return user

    def create_superuser(self, phone, password, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        return self.create_user(phone, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    phone = models.CharField(max_length=15, unique=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)
    is_superuser = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)

    objects = UserManager()

    USERNAME_FIELD = "phone"
    REQUIRED_FIELDS = []

    def __str__(self):
        return self.phone

    class Meta:
        verbose_name = "کاربر"
        verbose_name_plural = "کاربر ها"


class OTP(models.Model):
    phone = models.CharField(max_length=11)
    code = models.CharField(max_length=6)
    created_at = models.DateTimeField(auto_now_add=True)
    expires_at = models.DateTimeField()
    is_used = models.BooleanField(default=False)

    class Meta:
        db_table = 'otps'
        ordering = ['-created_at']
        verbose_name = "کد تایید "
        verbose_name_plural = "کد های تایید"

    def save(self, *args, **kwargs):
        if not self.code:
            self.code = str(random.randint(100000, 999999))
        if not self.expires_at:
            self.expires_at = timezone.now() + timezone.timedelta(minutes=2)
        super().save(*args, **kwargs)

    def is_valid(self):
        return not self.is_used and timezone.now() < self.expires_at

    def is_expired(self):
        return timezone.now() > self.expires_at



class Profile(models.Model):
    user = models.OneToOneField(
        User,
        on_delete=models.CASCADE,
        related_name="profile",
        verbose_name="کاربر"
    )

    phone = models.CharField(
        max_length=11,
        blank=True,
        null=True,
        verbose_name="شماره تماس"
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
        verbose_name = "پروفایل"
        verbose_name_plural = "پروفایل‌ها"




class Address(models.Model):
    profile = models.ForeignKey(
        Profile,
        on_delete=models.CASCADE,
        related_name="addresses",
        verbose_name="پروفایل"
    )

    title = models.CharField(
        max_length=100,
        verbose_name="عنوان آدرس",
        help_text="مثال: منزل، محل کار"
    )

    full_address = models.TextField(
        verbose_name="آدرس کامل",
        help_text="مثال: بلوار ولایت انتهای نگارستان ۱۵ منزل اسکینی طبقه دوم پلاک ۱۲"
    )

    is_default = models.BooleanField(
        default=False,
        verbose_name="آدرس پیش‌فرض"
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
        verbose_name = "آدرس"
        verbose_name_plural = "آدرس‌ها"
        ordering = ["-is_default", "-created_at"]
    #
    # def __str__(self):
    #     return f"{self.title} - {self.profile.user.username}"

    def save(self, *args, **kwargs):
        # اگر این آدرس پیش‌فرض است، بقیه را غیرفعال کن
        if self.is_default:
            Address.objects.filter(
                profile=self.profile,
                is_default=True
            ).exclude(pk=self.pk).update(is_default=False)
        super().save(*args, **kwargs)


# سیگنال برای ساخت خودکار Profile هنگام ثبت‌نام
@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def create_user_profile(sender, instance, created, **kwargs):
    if created:
        Profile.objects.create(user=instance)


@receiver(post_save, sender=settings.AUTH_USER_MODEL)
def save_user_profile(sender, instance, **kwargs):
    if hasattr(instance, 'profile'):
        instance.profile.save()







class ContactUs(models.Model):
    """
    مدل تماس با ما - برای دریافت پیام‌های کاربران
    """
    full_name = models.CharField(
        max_length=200,
        verbose_name='نام و نام خانوادگی',
        help_text='نام کامل فرستنده پیام'
    )
    email = models.EmailField(
        verbose_name='ایمیل',
        help_text='آدرس ایمیل برای پاسخگویی'
    )
    phone = models.CharField(
        max_length=11,
        verbose_name='شماره تماس',
        help_text='شماره موبایل 11 رقمی',
        blank=True,
        null=True
    )
    subject = models.CharField(
        max_length=300,
        verbose_name='موضوع پیام',
        help_text='عنوان یا موضوع اصلی پیام'
    )
    message = models.TextField(
        verbose_name='متن پیام',
        help_text='متن کامل پیام کاربر'
    )
    is_read = models.BooleanField(
        default=False,
        verbose_name='خوانده شده',
        help_text='آیا این پیام توسط ادمین خوانده شده؟'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ارسال'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )

    class Meta:
        verbose_name = 'پیام تماس با ما'
        verbose_name_plural = 'پیام‌های تماس با ما'
        ordering = ['-created_at']
        db_table = 'contact_us'

    def __str__(self):
        return f'{self.full_name} - {self.subject}'


class AboutUs(models.Model):
    """
    مدل درباره ما - برای نمایش اطلاعات شرکت/فروشگاه
    """
    title = models.CharField(
        max_length=300,
        verbose_name='عنوان صفحه',
        help_text='عنوان اصلی صفحه درباره ما',
        default='درباره ما'
    )
    short_description = models.TextField(
        verbose_name='توضیحات کوتاه',
        help_text='خلاصه‌ای از معرفی فروشگاه (حداکثر 500 کاراکتر)',
        max_length=500
    )
    full_description = CKEditor5Field(
        verbose_name='توضیحات کامل',
        help_text='متن کامل درباره فروشگاه با امکان فرمت‌بندی',
        config_name='extends'
    )
    mission = models.TextField(
        verbose_name='ماموریت ما',
        help_text='شرح ماموریت و هدف اصلی فروشگاه',
        blank=True,
        null=True
    )
    vision = models.TextField(
        verbose_name='چشم‌انداز ما',
        help_text='چشم‌انداز و اهداف آینده',
        blank=True,
        null=True
    )
    image = models.ImageField(
        upload_to='about_us/',
        verbose_name='تصویر اصلی',
        help_text='تصویر نمایشی صفحه درباره ما',
        blank=True,
        null=True
    )
    address = models.TextField(
        verbose_name='آدرس',
        help_text='آدرس کامل فروشگاه یا دفتر مرکزی',
        blank=True,
        null=True
    )
    phone = models.CharField(
        max_length=11,
        verbose_name='شماره تماس',
        help_text='شماره تماس اصلی',
        blank=True,
        null=True
    )
    email = models.EmailField(
        verbose_name='ایمیل',
        help_text='ایمیل رسمی فروشگاه',
        blank=True,
        null=True
    )
    working_hours = models.CharField(
        max_length=200,
        verbose_name='ساعات کاری',
        help_text='مثال: شنبه تا پنجشنبه 8 صبح تا 8 شب',
        blank=True,
        null=True
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
        help_text='نمایش این صفحه در سایت'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )

    class Meta:
        verbose_name = 'صفحه درباره ما'
        verbose_name_plural = 'درباره ما'
        db_table = 'about_us'

    def __str__(self):
        return self.title


class FAQ(models.Model):
    """
    مدل سوالات متداول - برای نمایش سوالات و جواب‌های رایج
    """
    question = models.CharField(
        max_length=500,
        verbose_name='سوال',
        help_text='متن سوال (حداکثر 500 کاراکتر)'
    )
    answer = CKEditor5Field(
        verbose_name='پاسخ',
        help_text='پاسخ کامل سوال با امکان فرمت‌بندی',
        config_name='extends'
    )
    category = models.CharField(
        max_length=100,
        verbose_name='دسته‌بندی',
        help_text='مثال: خرید، ارسال، پرداخت',
        choices=[
            ('general', 'عمومی'),
            ('order', 'سفارش و خرید'),
            ('payment', 'پرداخت'),
            ('shipping', 'ارسال'),
            ('return', 'مرجوعی'),
            ('account', 'حساب کاربری'),
            ('product', 'محصولات'),
        ],
        default='general'
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='اولویت نمایش',
        help_text='عدد کوچکتر = اولویت بالاتر (0, 1, 2, ...)'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال',
        help_text='نمایش این سوال در سایت'
    )
    created_at = models.DateTimeField(
        auto_now_add=True,
        verbose_name='تاریخ ایجاد'
    )
    updated_at = models.DateTimeField(
        auto_now=True,
        verbose_name='تاریخ بروزرسانی'
    )

    class Meta:
        verbose_name = 'سوال متداول'
        verbose_name_plural = 'سوالات متداول'
        ordering = ['order', '-created_at']
        db_table = 'faq'

    def __str__(self):
        return self.question


class SocialMedia(models.Model):
    """
    مدل شبکه‌های اجتماعی - برای نمایش لینک‌های شبکه‌های اجتماعی در فوتر
    """
    name = models.CharField(
        max_length=100,
        verbose_name='نام شبکه اجتماعی',
        help_text='مثال: اینستاگرام، تلگرام، واتساپ',
        choices=[
            ('instagram', 'اینستاگرام'),
            ('telegram', 'تلگرام'),
            ('whatsapp', 'واتساپ'),
            ('twitter', 'توییتر'),
            ('linkedin', 'لینکدین'),
            ('youtube', 'یوتیوب'),
            ('aparat', 'آپارات'),
        ]
    )
    url = models.URLField(
        verbose_name='آدرس لینک',
        help_text='لینک کامل شبکه اجتماعی'
    )
    icon_class = models.CharField(
        max_length=100,
        verbose_name='کلاس آیکون',
        help_text='مثال: fab fa-instagram',
        blank=True,
        null=True
    )
    order = models.PositiveIntegerField(
        default=0,
        verbose_name='اولویت نمایش',
        help_text='ترتیب نمایش در سایت'
    )
    is_active = models.BooleanField(
        default=True,
        verbose_name='فعال'
    )

    class Meta:
        verbose_name = 'شبکه اجتماعی'
        verbose_name_plural = 'شبکه‌های اجتماعی'
        ordering = ['order']
        db_table = 'social_media'

    def __str__(self):
        return self.get_name_display()
