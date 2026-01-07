from django.contrib import admin
from django.contrib.auth.admin import UserAdmin as BaseUserAdmin
from django.utils.translation import gettext_lazy as _
from .models import *


@admin.register(User)
class UserAdmin(BaseUserAdmin):
    ordering = ("-created_at",)
    list_display = (
        "phone",
        "is_active",
        "is_staff",
        "is_superuser",
        "created_at",
    )
    list_filter = ("is_active", "is_staff", "is_superuser")
    search_fields = ("phone",)

    fieldsets = (
        (_("اطلاعات اصلی"), {
            "fields": ("phone", "password")
        }),
        (_("دسترسی‌ها"), {
            "fields": ("is_active", "is_staff", "is_superuser", "groups", "user_permissions"),
        }),
        (_("زمان‌ها"), {
            "fields": ("last_login", "created_at"),
        }),
    )

    add_fieldsets = (
        (None, {
            "classes": ("wide",),
            "fields": (
                "phone",
                "password1",
                "password2",
                "is_active",
                "is_staff",
                "is_superuser",
            ),
        }),
    )

    readonly_fields = ("created_at", "last_login")

    filter_horizontal = ("groups", "user_permissions")


class AddressInline(admin.TabularInline):
    model = Address
    extra = 0

@admin.register(Profile)
class ProfileAdmin(admin.ModelAdmin):
    list_display = ['user', 'phone', 'created_at']
    inlines = [AddressInline]
    search_fields = ['user__username', 'phone']

@admin.register(Address)
class AddressAdmin(admin.ModelAdmin):
    list_display = ['title', 'profile', 'is_default', 'created_at']
    list_filter = ['is_default']
    search_fields = ['title', 'full_address', 'profile__user__username']

@admin.register(OTP)
class OTPAdmin(admin.ModelAdmin):
    list_display = ['code','phone']


@admin.register(ContactUs)
class ContactUsAdmin(admin.ModelAdmin):
    list_display = ['full_name', 'email', 'subject', 'is_read', 'created_at']
    list_filter = ['is_read', 'created_at']
    search_fields = ['full_name', 'email', 'subject', 'message']
    readonly_fields = ['created_at', 'updated_at']
    list_editable = ['is_read']
    date_hierarchy = 'created_at'

    fieldsets = (
        ('اطلاعات فرستنده', {
            'fields': ('full_name', 'email', 'phone')
        }),
        ('محتوای پیام', {
            'fields': ('subject', 'message')
        }),
        ('وضعیت', {
            'fields': ('is_read',)
        }),
        ('تاریخ و زمان', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(AboutUs)
class AboutUsAdmin(admin.ModelAdmin):
    list_display = ['title', 'is_active', 'updated_at']
    list_filter = ['is_active', 'created_at']
    search_fields = ['title', 'short_description']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('عنوان و توضیحات', {
            'fields': ('title', 'short_description', 'full_description')
        }),
        ('ماموریت و چشم‌انداز', {
            'fields': ('mission', 'vision'),
            'classes': ('collapse',)
        }),
        ('تصویر', {
            'fields': ('image',)
        }),
        ('اطلاعات تماس', {
            'fields': ('address', 'phone', 'email', 'working_hours')
        }),
        ('تنظیمات', {
            'fields': ('is_active',)
        }),
        ('تاریخ و زمان', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(FAQ)
class FAQAdmin(admin.ModelAdmin):
    list_display = ['question', 'category', 'order', 'is_active', 'created_at']
    list_filter = ['category', 'is_active', 'created_at']
    search_fields = ['question', 'answer']
    list_editable = ['order', 'is_active']
    readonly_fields = ['created_at', 'updated_at']

    fieldsets = (
        ('سوال و پاسخ', {
            'fields': ('question', 'answer')
        }),
        ('دسته‌بندی و ترتیب', {
            'fields': ('category', 'order')
        }),
        ('وضعیت', {
            'fields': ('is_active',)
        }),
        ('تاریخ و زمان', {
            'fields': ('created_at', 'updated_at'),
            'classes': ('collapse',)
        }),
    )


@admin.register(SocialMedia)
class SocialMediaAdmin(admin.ModelAdmin):
    list_display = ['name', 'url', 'order', 'is_active']
    list_filter = ['name', 'is_active']
    list_editable = ['order', 'is_active']

    fieldsets = (
        ('اطلاعات شبکه', {
            'fields': ('name', 'url', 'icon_class')
        }),
        ('تنظیمات', {
            'fields': ('order', 'is_active')
        }),
    )