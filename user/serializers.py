from rest_framework import serializers
from .models import StudentUserProfile, StudentUserPortfolio, PortfolioFile
from api.utils import generate_presigned_url
from django.conf import settings


class StudentUserProfileSerializer(serializers.ModelSerializer):
    profile_image = serializers.SerializerMethodField()
    univ_certificate = serializers.SerializerMethodField()

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
