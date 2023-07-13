from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from user.models import CompanyUser
from django.core.cache import cache


class CompanyVerificationSerializer(serializers.Serializer):
    business_number = serializers.CharField(max_length=10)
    ceo_name = serializers.CharField(max_length=10)
    start_date = serializers.DateField()
    corporate_number = serializers.CharField(max_length=13)


class CompanyManagerEmailVerificationSerializer(serializers.Serializer):
    manager_email = serializers.EmailField()
    auth_code = serializers.IntegerField()


class CompanyManagerPhoneVerificationSerializer(serializers.Serializer):
    manager_phone = serializers.CharField(max_length=20)
    auth_number = serializers.IntegerField()


class CompanyUserRegistrationSerializer(RegisterSerializer):
    manager_phone = serializers.CharField(max_length=20)
    manager_email = serializers.EmailField()
    business_number = serializers.CharField(max_length=10)
    ceo_name = serializers.CharField(max_length=10)
    start_date = serializers.DateField()
    corporate_number = serializers.CharField(max_length=13)

    def validate(self, attrs):
        super().validate(attrs)

        business_number = attrs.get("business_number", "")
        manager_email = attrs.get("manager_email", "")
        manager_phone = attrs.get("manager_phone", "")

        if (
            not cache.get(business_number + "_authenticated")
            or not cache.get(manager_email + "_authenticated")
            or not cache.get(manager_phone + "_authenticated")
        ):
            raise serializers.ValidationError(
                "회원가입 전 회사정보, 이메일, 휴대폰 인증이 모두 되어 있어야 합니다."
            )

        return attrs

    def custom_signup(self, request, user):
        manager_email = self.validated_data.get("manager_email", "")

        user.email = manager_email
        user.save()

        CompanyUser.objects.create(
            user=user,
            business_number=self.validated_data.get("business_number", ""),
            ceo_name=self.validated_data.get("ceo_name", ""),
            start_date=self.validated_data.get("start_date", ""),
            corporate_number=self.validated_data.get("corporate_number", ""),
            manager_email=manager_email,
            manager_phone=self.validated_data.get("manager_phone", ""),
        )
