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
