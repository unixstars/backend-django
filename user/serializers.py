from rest_framework import serializers
from .models import StudentUserProfile, StudentUserPortfolio, PortfolioFile
from api.utils import generate_presigned_url
from django.conf import settings


class StudentUserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUserProfile
        fields = [
            "id",
            "name",
            "profile_image",
            "birth",
            "phone_number",
            "university",
            "major",
            "univ_certificate",
            "bank",
            "account_number",
        ]

    def get_profile_image(self, obj):
        if obj.profile_image:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.profile_image)
            )

    def get_univ_certificate(self, obj):
        if obj.univ_certificate:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.univ_certificate)
            )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.profile_image:
            ret["profile_image"] = generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(instance.profile_image)
            )
        if instance.univ_certificate:
            ret["univ_certificate"] = generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(instance.univ_certificate)
            )
        return ret


class StudentUserProfileUpdateSerializer(serializers.ModelSerializer):
    name = serializers.CharField(required=False)
    profile_image = serializers.ImageField(required=False)
    birth = serializers.DateField(required=False)
    phone_number = serializers.CharField(required=False)
    university = serializers.CharField(required=False)
    major = serializers.CharField(required=False)
    univ_certificate = serializers.FileField(required=False)
    bank = serializers.CharField(required=False)
    account_number = serializers.CharField(required=False)

    class Meta:
        model = StudentUserProfile
        fields = [
            "id",
            "name",
            "profile_image",
            "birth",
            "phone_number",
            "university",
            "major",
            "univ_certificate",
            "bank",
            "account_number",
        ]

    def get_profile_image(self, obj):
        if obj.profile_image:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.profile_image)
            )

    def get_univ_certificate(self, obj):
        if obj.univ_certificate:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.univ_certificate)
            )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.profile_image:
            ret["profile_image"] = generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(instance.profile_image)
            )
        if instance.univ_certificate:
            ret["univ_certificate"] = generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(instance.univ_certificate)
            )
        return ret


class PortfolioFileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PortfolioFile
        fields = [
            "file",
        ]

    def get_file(self, obj):
        if obj.file:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.file)
            )

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.file:
            ret["file"] = generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(instance.file)
            )
        return ret


class StudentUserPortfolioSerializer(serializers.ModelSerializer):
    portfolio_file = PortfolioFileSerializer(many=True, required=False)

    class Meta:
        model = StudentUserPortfolio
        fields = [
            "id",
            "title",
            "content",
            "description",
            "portfolio_file",
        ]

    def create(self, validated_data):
        # portfolio_files_data를 validated_data에서 제거(StudentUserPortfolio 모델의 에러 발생 방지)
        portfolio_files_data = validated_data.pop("portfolio_file", [])
        student_user_portfolio = StudentUserPortfolio.objects.create(**validated_data)
        for portfolio_file_data in portfolio_files_data:
            PortfolioFile.objects.create(
                student_user_portfolio=student_user_portfolio, **portfolio_file_data
            )
        return student_user_portfolio


class StudentUserPortfolioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUserPortfolio
        fields = [
            "id",
            "title",
        ]
