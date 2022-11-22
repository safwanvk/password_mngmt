from datetime import timedelta
import re
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Password, Organization, Share
from django.contrib.auth.hashers import (
    make_password,
)
from .util import encrypt, decrypt
from django.utils import timezone
from django.contrib.auth.models import Permission
from django.conf import settings

class RegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirmpswd = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'confirmpswd', 'id')
        extra_kwargs = {
            'first_name': {'required': True},
            'last_name': {'required': True}
        }

    def validate(self, attrs):
        if attrs['password'] != attrs['confirmpswd']:
            raise serializers.ValidationError({"password": "Password fields didn't match."})

        return attrs

    def create(self, validated_data):
        user = User.objects.create(
            email = validated_data['email'],
            first_name = validated_data['first_name'],
            last_name = validated_data['last_name'],
        )

        user.set_password(validated_data['password'])
        user.save()
        
        return user


class PasswordSerializer(serializers.ModelSerializer):
    """
    Serializes a Password register object
    """
    password = serializers.CharField(write_only=True, validators=[validate_password])
    decrypt_password = serializers.SerializerMethodField(read_only=True)
    strength = serializers.SerializerMethodField(read_only=True)
    status = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Password
        fields = ('id', 'title', 'password', 'date', 'decrypt_password', 'strength', 
                  'duration_in_days', 'expired_at', 'status', 'created_by')

    def create(self, validated_data):
        """
        Create an return a new password
        """
        password = Password.objects.create(
            title=validated_data['title'],
            password=encrypt(validated_data['password']),
            duration_in_days=validated_data['duration_in_days'],
            expired_at=timezone.now() + timedelta(days=validated_data['duration_in_days']),
            created_by=self.context['request'].user
            )

        return password
    
    def update(self, instance, validated_data):
        """Handle updating password model"""
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.password = encrypt(password)
        if 'duration_in_days' in validated_data:
            instance.expired_at = instance.date + timedelta(days=validated_data['duration_in_days'])

        return super().update(instance, validated_data)
    
    def get_decrypt_password(self, obj):
        return decrypt(obj.password)
    
    def get_strength(self, obj):
        if(bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})',decrypt(obj.password)))==True):
            return "Strong"
        elif(bool(re.match('((\d*)([a-z]*)([A-Z]*)([!@#$%^&*]*).{8,30})',decrypt(obj.password)))==True):
            return "Weak"
    
    def get_status(self, obj):
        return 'Expired' if obj.expired_at <= timezone.now() else 'Not expired'

class  OrganizationSerializer(serializers.ModelSerializer):
    users = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Organization
        fields = '__all__'
    
    def get_users(self, obj):
        return User.objects.values_list('id', flat=True).filter(organizations=obj).distinct()


class  ShareSerializer(serializers.ModelSerializer):
    url = serializers.SerializerMethodField(read_only=True)
    class Meta:
        model = Share
        fields = '__all__'
    
    def get_url(self, obj):
        return '%s/api/shared_passwords/%s/' % (settings.BASE_URL, obj.password.id)


class  PermissionSerializer(serializers.ModelSerializer):
    content_type_name = serializers.SerializerMethodField('get_content_type_name', read_only=True)

    class Meta:
        model = Permission
        fields = '__all__'

    def get_content_type_name(self, obj):
        return obj.content_type.name
