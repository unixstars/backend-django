from rest_framework import serializers
from dj_rest_auth.registration.serializers import RegisterSerializer
from user.models import CompanyUser, StudentUser, User
from django.core.cache import cache
from api.utils import hash_function
from allauth.account.utils import assess_unique_email
from django.utils import timezone


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
    email = serializers.EmailField(required=False)
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

        # 회원탈퇴한 유저인지 확인
        try:
            user = User.objects.get(email=manager_email)
            if not user.is_active:
                raise serializers.ValidationError(
                    {"non_field_errors": ["회원탈퇴한 유저입니다."]}
                )
        except User.DoesNotExist:
            pass

        if assess_unique_email(manager_email):
            raise serializers.ValidationError(
                ("해당 이메일로 가입된 유저가 이미 존재합니다."),
            )
        manager_phone = attrs.get("manager_phone", "")

        if (
            not cache.get(hash_function(business_number) + "_authenticated")
            or not cache.get(hash_function(manager_email) + "_authenticated")
            or not cache.get(hash_function(manager_phone) + "_authenticated")
        ):
            raise serializers.ValidationError(
                "회원가입 전 회사정보, 이메일, 휴대폰 인증이 모두 되어 있어야 합니다."
            )

        return attrs

    def save(self, request):
        self.validated_data["email"] = self.validated_data.get("manager_email", "")
        user = super().save(request)
        user.is_company_user = True
        user.save()

        CompanyUser.objects.create(
            user=user,
            business_number=self.validated_data.get("business_number", ""),
            ceo_name=self.validated_data.get("ceo_name", ""),
            start_date=self.validated_data.get("start_date", ""),
            corporate_number=self.validated_data.get("corporate_number", ""),
            manager_email=self.validated_data.get("manager_email", ""),
            manager_phone=self.validated_data.get("manager_phone", ""),
        )
        return user


class TestCompanyUserRegistrationSerializer(RegisterSerializer):
    email = serializers.EmailField(required=False)
    manager_phone = serializers.CharField(max_length=20)
    manager_email = serializers.EmailField()
    business_number = serializers.CharField(max_length=10)
    ceo_name = serializers.CharField(max_length=10)
    start_date = serializers.DateField(required=False)
    corporate_number = serializers.CharField(max_length=13)

    def validate(self, attrs):
        super().validate(attrs)
        manager_email = attrs.get("manager_email", "")

        # 회원탈퇴한 유저인지 확인
        try:
            user = User.objects.get(email=manager_email)
            if not user.is_active:
                raise serializers.ValidationError(
                    {"non_field_errors": ["회원탈퇴한 유저입니다."]}
                )
        except User.DoesNotExist:
            pass

        if assess_unique_email(manager_email):
            raise serializers.ValidationError(
                "해당 이메일로 가입된 유저가 이미 존재합니다."
            )

        return attrs

    def save(self, request):
        self.validated_data["email"] = self.validated_data.get("manager_email", "")
        user = super().save(request)
        user.is_company_user = True
        user.save()

        CompanyUser.objects.create(
            user=user,
            business_number=self.validated_data.get("business_number", ""),
            ceo_name=self.validated_data.get("ceo_name", ""),
            start_date=self.validated_data.get("start_date", timezone.now().date()),
            corporate_number=self.validated_data.get("corporate_number", ""),
            manager_email=self.validated_data.get("manager_email", ""),
            manager_phone=self.validated_data.get("manager_phone", ""),
        )
        return user


class CompanyUserInfoFindVerificationSerializer(serializers.Serializer):
    register_phone = serializers.CharField(max_length=20)
    auth_number = serializers.IntegerField()


class TestStudentRegisterSerializer(RegisterSerializer):
    def custom_signup(self, request, user):
        if not hasattr(user, "student_user"):
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

    def save(self, request):
        user = super().save(request)
        self.custom_signup(request, user)
        return user


class UserDeactivateSerializer(serializers.Serializer):
    confirm = serializers.BooleanField()

    def validate_confirm(self, value):
        if not value:
            raise serializers.ValidationError("confirm이 True여야 합니다.")
        return value
