import re
from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from .models import User, Password, Organization
from django.contrib.auth.hashers import (
    make_password,
)
from .util import encrypt, decrypt

class RegisterSerializer(serializers.ModelSerializer):
    
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])
    confirmpswd = serializers.CharField(write_only=True, required=True)

    class Meta:
        model = User
        fields = ('first_name', 'last_name', 'email', 'password', 'confirmpswd')
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
    class Meta:
        model = Password
        fields = ('id', 'title', 'password', 'date', 'decrypt_password', 'strength')

    def create(self, validated_data):
        """
        Create an return a new password
        """
        password = Password.objects.create(
            title=validated_data['title'],
            password=encrypt(validated_data['password'])
            )

        return password
    
    def update(self, instance, validated_data):
        """Handle updating password model"""
        if 'password' in validated_data:
            password = validated_data.pop('password')
            instance.password = encrypt(password)

        return super().update(instance, validated_data)
    
    def get_decrypt_password(self, obj):
        return decrypt(obj.password)
    
    def get_strength(self, obj):
        if(bool(re.match('((?=.*\d)(?=.*[a-z])(?=.*[A-Z])(?=.*[!@#$%^&*]).{8,30})',decrypt(obj.password)))==True):
            return "Strong"
        elif(bool(re.match('((\d*)([a-z]*)([A-Z]*)([!@#$%^&*]*).{8,30})',decrypt(obj.password)))==True):
            return "Weak"

class  OrganizationSerializer(serializers.ModelSerializer):
    class Meta:
        model = Organization
        fields = '__all__'


