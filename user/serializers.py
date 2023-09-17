from rest_framework import serializers
from .models import StudentUserProfile, StudentUserPortfolio, PortfolioFile, CompanyUser
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
            "social_number",
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
    social_number = serializers.CharField(required=False)
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
            "social_number",
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


class StudentUserProfileShowSerializer(serializers.ModelSerializer):
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
    id = serializers.IntegerField(required=False)

    class Meta:
        model = PortfolioFile
        fields = [
            "id",
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


class StudentUserPortfolioUpdateSerializer(serializers.ModelSerializer):
    title = serializers.CharField(required=False)
    content = serializers.CharField(required=False)
    description = serializers.CharField(required=False)
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

    def update(self, instance, validated_data):
        portfolio_files_data = validated_data.pop("portfolio_file", [])
        # portfolio_file을 제외한 StudentUserPortfolio 업데이트
        instance.title = validated_data.get("title", instance.title)
        instance.content = validated_data.get("content", instance.content)
        instance.description = validated_data.get("description", instance.description)
        instance.save()

        for file_data in portfolio_files_data:
            file_id = file_data.get("id", None)

            # 만약 ID가 제공되면, 해당 객체를 업데이트
            if file_id:
                portfolio_file = PortfolioFile.objects.get(
                    id=file_id, student_user_portfolio=instance
                )
                if "file" in file_data:
                    portfolio_file.file = file_data["file"]
                    portfolio_file.save()
            # ID가 없다면, 새로운 객체를 생성
            else:
                PortfolioFile.objects.create(
                    student_user_portfolio=instance, **file_data
                )

        return instance


class StudentUserPortfolioListSerializer(serializers.ModelSerializer):
    class Meta:
        model = StudentUserPortfolio
        fields = [
            "id",
            "title",
        ]


class CompanyUserInfoSerializer(serializers.ModelSerializer):
    class Meta:
        model = CompanyUser
        fields = [
            "business_number",
            "ceo_name",
            "start_date",
            "corporate_number",
            "manager_email",
            "manager_phone",
        ]


class CompanyUserInfoChangePhoneVerificationSerializer(serializers.Serializer):
    new_manager_phone = serializers.CharField(max_length=20)
    auth_number = serializers.IntegerField()


class CompanyUserInfoChangeSerializer(serializers.ModelSerializer):
    new_password1 = serializers.CharField(write_only=True, required=False)
    new_password2 = serializers.CharField(write_only=True, required=False)
    new_manager_phone = serializers.CharField(required=False)

    class Meta:
        model = CompanyUser
        fields = ["new_password1", "new_password2", "new_manager_phone"]

    def validate(self, data):
        new_password1 = data.get("new_password1")
        new_password2 = data.get("new_password2")

        if new_password1 or new_password2:
            if not new_password1 or not new_password2:
                raise serializers.ValidationError("두 비밀번호 모두 입력해야 합니다.")
            if new_password1 != new_password2:
                raise serializers.ValidationError("비밀번호가 일치하지 않습니다.")

        return data
