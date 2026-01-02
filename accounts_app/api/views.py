import logging
import random
from rest_framework import status
from rest_framework.views import APIView
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from .serializers import *
import requests
from django.utils import timezone
from django.shortcuts import render,redirect
from accounts_app.models import OTP, User
from django.contrib.auth import login
from rest_framework.permissions import AllowAny
from django.utils import timezone
from datetime import timedelta

class ProfileView(APIView):
    permission_classes = [IsAuthenticated]


    def get(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile)
        return Response(serializer.data)

    def patch(self, request):
        profile = request.user.profile
        serializer = ProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressListCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        addresses = request.user.profile.addresses.all()
        serializer = AddressSerializer(addresses, many=True)
        return Response(serializer.data)

    def post(self, request):
        serializer = AddressSerializer(data=request.data)
        if serializer.is_valid():
            serializer.save(profile=request.user.profile)
            return Response(serializer.data, status=status.HTTP_201_CREATED)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)


class AddressDetailView(APIView):
    permission_classes = [IsAuthenticated]

    def get_object(self, pk, user):
        try:
            return Address.objects.get(pk=pk, profile=user.profile)
        except Address.DoesNotExist:
            return None

    def get(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response(
                {"error": "آدرس یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AddressSerializer(address)
        return Response(serializer.data)

    def patch(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response(
                {"error": "آدرس یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )
        serializer = AddressSerializer(address, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        address = self.get_object(pk, request.user)
        if not address:
            return Response(
                {"error": "آدرس یافت نشد"},
                status=status.HTTP_404_NOT_FOUND
            )
        address.delete()
        return Response(
            {"message": "آدرس با موفقیت حذف شد"},
            status=status.HTTP_204_NO_CONTENT
        )

logger = logging.getLogger(__name__)


class SendOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        logger.info(f"Request data: {request.data}")
        logger.info(f"Content-Type: {request.content_type}")

        serializer = SendOTPSerializer(data=request.data)

        if not serializer.is_valid():
            logger.error(f"Validation errors: {serializer.errors}")
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']
        logger.info(f"Processing OTP for phone: {phone}")

        try:
            # حذف کدهای قبلی
            deleted_count = OTP.objects.filter(phone=phone).delete()[0]
            logger.info(f"Deleted {deleted_count} old OTP records")

            # ساخت کد تصادفی
            code = str(random.randint(100000, 999999))
            expires_at = timezone.now() + timedelta(minutes=2)

            # ذخیره در دیتابیس
            otp = OTP.objects.create(
                phone=phone,
                code=code,
                expires_at=expires_at
            )
            logger.info(f"OTP created with ID: {otp.id}")

            # چاپ کد در Console برای تست
            print(f"\n{'=' * 50}")
            print(f"کد OTP برای {phone}: {code}")
            print(f"انقضا: {expires_at}")
            print(f"{'=' * 50}\n")

            return Response({
                'detail': 'کد تایید ارسال شد'
            }, status=status.HTTP_200_OK)

        except Exception as e:
            logger.error(f"Error in SendOTP: {str(e)}", exc_info=True)
            return Response({
                'detail': 'خطا در ارسال کد تایید'
            }, status=status.HTTP_500_INTERNAL_SERVER_ERROR)


# views.py - VerifyOTPAPIView

class VerifyOTPAPIView(APIView):
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = VerifyOTPSerializer(data=request.data)

        if not serializer.is_valid():
            return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

        phone = serializer.validated_data['phone']
        code = serializer.validated_data['code']

        try:
            otp = OTP.objects.filter(phone=phone).latest('created_at')
        except OTP.DoesNotExist:
            return Response({
                'detail': 'کد تایید یافت نشد'
            }, status=status.HTTP_400_BAD_REQUEST)

        if otp.is_expired():
            otp.delete()
            return Response({
                'detail': 'کد تایید منقضی شده است'
            }, status=status.HTTP_400_BAD_REQUEST)

        if otp.code != code:
            return Response({
                'detail': 'کد تایید اشتباه است'
            }, status=status.HTTP_400_BAD_REQUEST)

        # ✅ فقط phone رو بفرست، defaults نمی‌خواد
        user, created = User.objects.get_or_create(phone=phone)

        otp.delete()
        login(request, user, backend='django.contrib.auth.backends.ModelBackend')

        return Response({
            'detail': 'ورود با موفقیت انجام شد' if not created else 'ثبت‌نام با موفقیت انجام شد',
            'type': 'login' if not created else 'register'
        }, status=status.HTTP_200_OK)

def auth_page(request):
    """نمایش صفحه ورود/ثبت نام"""
    if request.user.is_authenticated:
        return redirect('home')  # اگر لاگین است به صفحه اصلی برود
    return render(request, 'accounts_app/register.html')