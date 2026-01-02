from rest_framework import serializers
from accounts_app.models import Profile, Address,User
import re
from django.contrib.auth import get_user_model
from accounts_app.models import *

class AddressSerializer(serializers.ModelSerializer):
    class Meta:
        model = Address
        fields = ['id', 'title', 'full_address', 'is_default', 'created_at']
        read_only_fields = ['id', 'created_at']


class ProfileSerializer(serializers.ModelSerializer):
    addresses = AddressSerializer(many=True, read_only=True)
    username = serializers.CharField(source='user.username', read_only=True)
    email = serializers.EmailField(source='user.email', read_only=True)

    class Meta:
        model = Profile
        fields = ['id', 'username', 'email', 'phone', 'addresses', 'created_at']
        read_only_fields = ['id', 'created_at']

User = get_user_model()


class SendOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, min_length=11)


    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('شماره تلفن فقط باید شامل اعداد باشد')
        if not value.startswith('0'):
            raise serializers.ValidationError('شماره تلفن باید با 0 شروع شود')
        return value


class VerifyOTPSerializer(serializers.Serializer):
    phone = serializers.CharField(max_length=11, min_length=11)
    code = serializers.CharField(max_length=6, min_length=6)

    def validate_phone(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('شماره تلفن فقط باید شامل اعداد باشد')
        if not value.startswith('0'):
            raise serializers.ValidationError('شماره تلفن باید با 0 شروع شود')
        return value

    def validate_code(self, value):
        if not value.isdigit():
            raise serializers.ValidationError('کد تایید فقط باید شامل اعداد باشد')
        return value