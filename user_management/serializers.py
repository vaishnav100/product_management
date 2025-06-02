from rest_framework import serializers
from user_management.models import User, Token
from django.contrib.auth import get_user_model, authenticate, login
import re

class RegisterUserSerializer(serializers.ModelSerializer):
    is_admin_approve = serializers.BooleanField(default=False)
    created_at = serializers.DateTimeField(read_only=True)
    updated_at = serializers.DateTimeField(read_only=True)
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)
    username = serializers.CharField(max_length=150, required=True)
    email = serializers.EmailField(required=False)

    def validate_password(self, value):
        if len(value) < 8:
            raise serializers.ValidationError("Password must be at least 8 characters long.")
        if not re.search(r"[A-Z]", value):
            raise serializers.ValidationError("Password must contain at least one uppercase letter.")
        if not re.search(r"[a-z]", value):
            raise serializers.ValidationError("Password must contain at least one lowercase letter.")
        if not re.search(r"[0-9]", value):
            raise serializers.ValidationError("Password must contain at least one digit.")
        if not re.search(r"[!@#$%^&*(),.?\":{}|<>]", value):
            raise serializers.ValidationError("Password must contain at least one special character.")
        return value

    def validate_username(self, value):
        if User.objects.filter(username=value).exists():
            raise serializers.ValidationError("Username already exists. Please choose a different username.")
        return value

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user

    def update(self, instance, validated_data):
        instance.username = validated_data.get('username', instance.username)
        instance.email = validated_data.get('email', instance.email)
        instance.is_admin_approve = validated_data.get('is_admin_approve', instance.is_admin_approve)

        password = validated_data.get('password', None)
        if password:
            instance.set_password(password)

        instance.save()
        return instance

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'password', 'is_admin_approve', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_admin_approve']


class LoginUserSerializer(serializers.ModelSerializer):
    username = serializers.CharField(max_length=150, required=True)
    password = serializers.CharField(write_only=True, required=True, allow_blank=False)

    def validate(self, attrs):
        username = attrs.get('username')
        password = attrs.get('password')

        user = authenticate(username=username, password=password)
        if user is None :
            raise serializers.ValidationError("Invalid username or password.")

        # if not user.is_admin_approve:
        #     raise serializers.ValidationError("User account is not approved by admin.")
        
        attrs['user'] = user
        
        return attrs

    class Meta:
        model = User
        fields = ['username', 'password']                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                                   


class TokenSerializer(serializers.ModelSerializer):
    access_token = serializers.CharField(read_only=True)
    refresh_token = serializers.CharField(read_only=True)
    user = serializers.PrimaryKeyRelatedField(read_only=True)
    
    class Meta:
        model = Token
        fields = ['id', 'user', 'access_token', 'refresh_token']

class UserSerializer(serializers.ModelSerializer):

    class Meta:
        model = User
        fields = ['id', 'username', 'email', 'is_admin_approve', 'created_at', 'updated_at']
        read_only_fields = ['id', 'created_at', 'updated_at', 'is_admin_approve']