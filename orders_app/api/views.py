# orders_app/views.py

from rest_framework import viewsets, status
from rest_framework.decorators import action
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.db import transaction
from orders_app.models import Order, Coupon
from cart_app.models import Cart
from .serializers import (
    OrderListSerializer,
    OrderDetailSerializer,
    CouponValidationSerializer,
    CheckoutSerializer
)
import traceback


class OrderViewSet(viewsets.ReadOnlyModelViewSet):
    """ویوست مدیریت سفارشات"""
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        return Order.objects.filter(user=self.request.user).prefetch_related('items')

    def get_serializer_class(self):
        if self.action == 'list':
            return OrderListSerializer
        return OrderDetailSerializer

    @action(detail=False, methods=['post'], url_path='validate-coupon')
    def validate_coupon(self, request):
        """بررسی اعتبار کوپن"""
        serializer = CouponValidationSerializer(
            data=request.data,
            context={'request': request}
        )

        if serializer.is_valid():
            code = serializer.validated_data['code']

            try:
                coupon = Coupon.objects.get(code=code)
                cart = Cart.objects.get(user=request.user)
                cart_total = cart.total_price

                discount = int(coupon.calculate_discount(cart_total))
                final_total = cart_total - discount

                return Response({
                    'valid': True,
                    'message': 'کوپن معتبر است',
                    'discount_amount': discount,
                    'final_total': final_total,
                    'coupon_details': {
                        'code': coupon.code,
                        'discount_percentage': float(coupon.discount_percentage),
                        'description': coupon.description
                    }
                })
            except (Coupon.DoesNotExist, Cart.DoesNotExist):
                return Response({
                    'valid': False,
                    'message': 'خطا در پردازش اطلاعات'
                }, status=status.HTTP_400_BAD_REQUEST)

        return Response({
            'valid': False,
            'message': serializer.errors.get('code', ['خطای نامشخص'])[0]
        }, status=status.HTTP_400_BAD_REQUEST)

    @action(detail=False, methods=['post'], url_path='checkout')
    def checkout(self, request):
        """ثبت سفارش نهایی"""
        serializer = CheckoutSerializer(
            data=request.data,
            context={'request': request}
        )

        if not serializer.is_valid():
            return Response({
                'success': False,
                'errors': serializer.errors
            }, status=status.HTTP_400_BAD_REQUEST)

        try:
            with transaction.atomic():
                order = serializer.save()

            return Response({
                'success': True,
                'message': 'سفارش شما با موفقیت ثبت شد',
                'order': OrderDetailSerializer(order).data
            }, status=status.HTTP_201_CREATED)

        except ValueError as e:
            return Response({
                'success': False,
                'message': str(e)
            }, status=status.HTTP_400_BAD_REQUEST)

        except Exception as e:
            print("=== CHECKOUT ERROR ===")
            print(f"Error Type: {type(e).__name__}")
            print(f"Error Message: {str(e)}")
            print("Full Traceback:")
            print(traceback.format_exc())
            print("=== END ERROR ===")

            return Response({
                'success': False,
                'message': f'خطا در ثبت سفارش: {str(e)}'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)

    @action(detail=True, methods=['post'], url_path='cancel')
    def cancel_order(self, request, pk=None):
        """لغو سفارش"""
        order = self.get_object()

        if order.status not in ['pending', 'paid']:
            return Response({
                'success': False,
                'message': 'امکان لغو این سفارش وجود ندارد'
            }, status=status.HTTP_400_BAD_REQUEST)

        with transaction.atomic():
            order.status = 'cancelled'
            order.save()

        return Response({
            'success': True,
            'message': 'سفارش با موفقیت لغو شد'
        })


@action(detail=True, methods=['get'])
def detail(self, request, pk=None):
    """دریافت جزئیات سفارش"""
    order = self.get_object()

    items = [{
        'id': item.id,
        'product_name': item.product.name,
        'product_image': item.product.image.url if item.product.image else '',
        'price': str(item.price),
        'quantity': item.quantity,
        'total_price': str(item.total_price),
    } for item in order.items.all()]

    return Response({
        'success': True,
        'order': {
            'id': order.id,
            'order_number': order.order_number,
            'status': order.status,
            'subtotal': str(order.subtotal),
            'discount_amount': str(order.discount_amount),
            'total_price': str(order.total_price),
            'items': items,
            'address': {
                'title': order.address.title,
                'full_address': order.address.full_address,
            } if order.address else None,
        }
    })
