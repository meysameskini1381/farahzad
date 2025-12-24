# orders_app/admin.py
from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from django.utils import timezone
from .models import Order, OrderItem, Coupon, CouponUsage


class OrderItemInline(admin.TabularInline):
    model = OrderItem
    extra = 0
    readonly_fields = ['product', 'product_name', 'product_image', 'quantity', 'price', 'total_price']
    can_delete = False

    def has_add_permission(self, request, obj=None):
        return False


@admin.register(Order)
class OrderAdmin(admin.ModelAdmin):
    list_display = [
        'order_number',
        'user_link',
        'status_badge',
        'total_amount_display',
        'items_count',
        'created_at',
        'paid_at'
    ]

    list_filter = [
        'status',
        'created_at',
        'paid_at',
        ('coupon', admin.EmptyFieldListFilter)
    ]

    search_fields = [
        'order_number',
        'user__username',
        'user__email',
        'coupon_code'
    ]

    readonly_fields = [
        'order_number',
        'user',
        'address_snapshot_display',
        'subtotal',
        'discount_amount',
        'shipping_cost',
        'total_amount',
        'created_at',
        'updated_at',
        'paid_at',
        'coupon_info'
    ]

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                'order_number',
                'user',
                'status',
                'created_at',
                'updated_at'
            )
        }),
        ('اطلاعات آدرس', {
            'fields': (
                'address',
                'address_snapshot_display'
            )
        }),
        ('اطلاعات مالی', {
            'fields': (
                'subtotal',
                'discount_amount',
                'shipping_cost',
                'total_amount',
                'paid_at'
            )
        }),
        ('کوپن تخفیف', {
            'fields': (
                'coupon',
                'coupon_code',
                'coupon_info'
            ),
            'classes': ('collapse',)
        }),
        ('یادداشت‌ها', {
            'fields': (
                'notes',
                'admin_notes'
            ),
            'classes': ('collapse',)
        })
    )

    inlines = [OrderItemInline]

    actions = [
        'mark_as_paid',
        'mark_as_processing',
        'mark_as_shipping',
        'mark_as_delivered',
        'mark_as_cancelled'
    ]

    def user_link(self, obj):
        url = reverse('admin:accounts_app_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.phone)

    user_link.short_description = 'کاربر'

    def status_badge(self, obj):
        colors = {
            'pending': '#ffc107',
            'paid': '#28a745',
            'processing': '#17a2b8',
            'shipping': '#007bff',
            'delivered': '#28a745',
            'cancelled': '#dc3545',
            'returned': '#6c757d'
        }
        color = colors.get(obj.status, '#6c757d')
        return format_html(
            '<span style="background-color: {}; color: white; padding: 5px 10px; border-radius: 3px;">{}</span>',
            color,
            obj.get_status_display()
        )

    status_badge.short_description = 'وضعیت'

    def total_amount_display(self, obj):
        return f"{obj.total_amount:,} تومان"

    total_amount_display.short_description = 'مبلغ کل'

    def address_snapshot_display(self, obj):
        if obj.address_snapshot:
            return format_html(
                '<div style="line-height: 1.6;">'
                '<strong>عنوان:</strong> {}<br>'
                '<strong>آدرس:</strong> {}'
                '</div>',
                obj.address_snapshot.get('title', '-'),
                obj.address_snapshot.get('full_address', '-')
            )
        return '-'

    address_snapshot_display.short_description = 'آدرس ثبت شده'

    def coupon_info(self, obj):
        if obj.coupon:
            return format_html(
                '<div style="line-height: 1.6;">'
                '<strong>کد:</strong> {}<br>'
                '<strong>تخفیف:</strong> {} تومان<br>'
                '<strong>درصد:</strong> {}%'
                '</div>',
                obj.coupon.code,
                f"{obj.discount_amount:,}",
                obj.coupon.discount_percentage
            )
        return 'بدون کوپن'

    coupon_info.short_description = 'جزئیات کوپن'

    @admin.action(description='تغییر وضعیت به پرداخت شده')
    def mark_as_paid(self, request, queryset):
        updated = queryset.filter(status='pending').update(
            status='paid',
            paid_at=timezone.now()
        )
        self.message_user(request, f'{updated} سفارش به وضعیت پرداخت شده تغییر کرد.')

    @admin.action(description='تغییر وضعیت به در حال پردازش')
    def mark_as_processing(self, request, queryset):
        updated = queryset.update(status='processing')
        self.message_user(request, f'{updated} سفارش به وضعیت در حال پردازش تغییر کرد.')

    @admin.action(description='تغییر وضعیت به در حال ارسال')
    def mark_as_shipping(self, request, queryset):
        updated = queryset.update(status='shipping')
        self.message_user(request, f'{updated} سفارش به وضعیت در حال ارسال تغییر کرد.')

    @admin.action(description='تغییر وضعیت به تحویل داده شده')
    def mark_as_delivered(self, request, queryset):
        updated = queryset.update(status='delivered')
        self.message_user(request, f'{updated} سفارش به وضعیت تحویل داده شده تغییر کرد.')

    @admin.action(description='تغییر وضعیت به لغو شده')
    def mark_as_cancelled(self, request, queryset):
        updated = queryset.update(status='cancelled')
        self.message_user(request, f'{updated} سفارش لغو شد.')


@admin.register(OrderItem)
class OrderItemAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'order_link',
        'product_link',
        'quantity',
        'price_display',
        'total_price_display'
    ]

    list_filter = ['created_at']

    search_fields = [
        'order__order_number',
        'product__title',
        'product_name'
    ]

    readonly_fields = [
        'order',
        'product',
        'product_name',
        'product_image',
        'quantity',
        'price',
        'total_price',
        'created_at'
    ]

    def order_link(self, obj):
        url = reverse('admin:orders_app_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)

    order_link.short_description = 'سفارش'

    def product_link(self, obj):
        url = reverse('admin:products_app_product_change', args=[obj.product.id])
        return format_html('<a href="{}">{}</a>', url, obj.product.title)

    product_link.short_description = 'محصول'

    def price_display(self, obj):
        return f"{obj.price:,} تومان"

    price_display.short_description = 'قیمت واحد'

    def total_price_display(self, obj):
        return f"{obj.total_price:,} تومان"

    total_price_display.short_description = 'قیمت کل'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False


@admin.register(Coupon)
class CouponAdmin(admin.ModelAdmin):
    list_display = [
        'code',
        'discount_badge',
        'usage_display',
        'validity_badge',
        'is_active',
        'valid_from',
        'valid_to'
    ]

    list_filter = [
        'is_active',
        'valid_from',
        'valid_to',
        'created_at'
    ]

    search_fields = ['code', 'description']

    fieldsets = (
        ('اطلاعات اصلی', {
            'fields': (
                'code',
                'description',
                'is_active'
            )
        }),
        ('تخفیف', {
            'fields': (
                'discount_percentage',
                'discount_amount',
                'max_discount_amount',
                'min_purchase_amount'
            )
        }),
        ('محدودیت استفاده', {
            'fields': (
                'usage_limit',
                'used_count',
                'per_user_limit'
            )
        }),
        ('اعتبار زمانی', {
            'fields': (
                'valid_from',
                'valid_to'
            )
        }),
        ('تاریخ‌ها', {
            'fields': (
                'created_at',
                'updated_at'
            ),
            'classes': ('collapse',)
        })
    )

    readonly_fields = ['used_count', 'created_at', 'updated_at']

    actions = ['activate_coupons', 'deactivate_coupons']

    def discount_badge(self, obj):
        if obj.discount_amount:
            return format_html(
                '<span style="color: #28a745; font-weight: bold;">{:,} تومان</span>',
                obj.discount_amount
            )
        return format_html(
            '<span style="color: #007bff; font-weight: bold;">{}%</span>',
            obj.discount_percentage
        )

    discount_badge.short_description = 'میزان تخفیف'

    def usage_display(self, obj):
        percentage = (obj.used_count / obj.usage_limit * 100) if obj.usage_limit > 0 else 0
        color = '#28a745' if percentage < 70 else '#ffc107' if percentage < 90 else '#dc3545'

        return format_html(
            '<div style="line-height: 1.6;">'
            '{} / {} <span style="color: {};">({}%)</span>'
            '</div>',
            obj.used_count,
            obj.usage_limit,
            color,
            int(percentage)
        )

    usage_display.short_description = 'استفاده شده'

    def validity_badge(self, obj):
        if obj.is_valid():
            return format_html(
                '<span style="background-color: #28a745; color: white; padding: 5px 10px; border-radius: 3px;">معتبر</span>'
            )
        return format_html(
            '<span style="background-color: #dc3545; color: white; padding: 5px 10px; border-radius: 3px;">نامعتبر</span>'
        )

    validity_badge.short_description = 'وضعیت'

    @admin.action(description='فعال کردن کوپن‌های انتخابی')
    def activate_coupons(self, request, queryset):
        updated = queryset.update(is_active=True)
        self.message_user(request, f'{updated} کوپن فعال شد.')

    @admin.action(description='غیرفعال کردن کوپن‌های انتخابی')
    def deactivate_coupons(self, request, queryset):
        updated = queryset.update(is_active=False)
        self.message_user(request, f'{updated} کوپن غیرفعال شد.')


@admin.register(CouponUsage)
class CouponUsageAdmin(admin.ModelAdmin):
    list_display = [
        'id',
        'user_link',
        'coupon_link',
        'order_link',
        'used_at'
    ]

    list_filter = ['used_at', 'coupon']

    search_fields = [
        'user__username',
        'coupon__code',
        'order__order_number'
    ]

    readonly_fields = [
        'user',
        'coupon',
        'order',
        'used_at'
    ]

    def user_link(self, obj):
        url = reverse('admin:accounts_app_user_change', args=[obj.user.id])
        return format_html('<a href="{}">{}</a>', url, obj.user.username)

    user_link.short_description = 'کاربر'

    def coupon_link(self, obj):
        url = reverse('admin:orders_app_coupon_change', args=[obj.coupon.id])
        return format_html('<a href="{}">{}</a>', url, obj.coupon.code)

    coupon_link.short_description = 'کوپن'

    def order_link(self, obj):
        url = reverse('admin:orders_app_order_change', args=[obj.order.id])
        return format_html('<a href="{}">{}</a>', url, obj.order.order_number)

    order_link.short_description = 'سفارش'

    def has_add_permission(self, request):
        return False

    def has_delete_permission(self, request, obj=None):
        return False
