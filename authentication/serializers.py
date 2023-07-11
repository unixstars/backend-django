"""
from user.models import User
from rest_framework import serializers


class UserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        user = User.objects.create_user(**validated_data)
        return user


class GeneralUserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ("email", "password", "username")
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["user_type"] = "general"
        user = User.objects.create_user(**validated_data)
        return user


class CompanyUserAuthSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = (
            "email",
            "password",
            "username",
            "company_name",
            "business_number",
            "manager_email",
            "manager_phone",
        )
        extra_kwargs = {"password": {"write_only": True}}

    def create(self, validated_data):
        validated_data["user_type"] = "company"
        user = User.objects.create_user(**validated_data)
        return user


class RefreshTokenSerializer(serializers.Serializer):
    refresh_token = serializers.CharField(required=True)
"""
from user.models import User, StudentUser
from rest_framework import serializers


# Test
class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = User
        fields = ["email", "password"]


# Test
class CompanyUserSerializer(serializers.ModelSerializer):
    email = serializers.SerializerMethodField()
    password = serializers.SerializerMethodField()

    class Meta:
        model = StudentUser
        fields = [
            "email",
            "password",
            "business_number",
            "ceo_name",
            "start_date",
            "corporate_number",
            "manager_phone",
            "manager_email",
        ]

    def get_email(self, obj):
        email = obj.user.email
        return email

    def get_password(self, obj):
        password = obj.user.password
        return password
