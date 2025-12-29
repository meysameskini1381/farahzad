from django.shortcuts import render, get_object_or_404
from django.contrib.auth.decorators import login_required
from orders_app.models import Order



@login_required
def order_detail(request, order_id):
    """نمایش جزئیات سفارش"""
    order = get_object_or_404(
        Order.objects.prefetch_related('items__product'),
        id=order_id,
        user=request.user
    )

    # محاسبه مقادیر
    items = order.items.all()
    subtotal = sum(item.total_price for item in items)
    discount = order.discount_amount if hasattr(order, 'discount_amount') else 0
    total = subtotal - discount

    context = {
        'order': order,
        'items': items,
        'address': order.address,
        'subtotal': subtotal,
        'discount': discount,
        'total': total,
    }
    return render(request, 'orders_app/order_detail.html', context)