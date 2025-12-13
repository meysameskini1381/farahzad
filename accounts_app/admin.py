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
