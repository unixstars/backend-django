from django.conf import settings
from rest_framework import serializers
from .models import Board, Activity, Scrap, Form, Suggestion
from api.utils import generate_presigned_url
from api.serializers import DurationFieldInISOFormat
from django.utils import timezone
from django.db import transaction
from datetime import timedelta
from user.serializers import (
    StudentUserProfileSerializer,
    StudentUserPortfolioListSerializer,
)
from user.models import StudentUserProfile, StudentUserPortfolio
from user.serializers import PortfolioFileSerializer


class BoardSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    scrap_count = serializers.SerializerMethodField()
    d_day = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "logo",
            "banner",
            "title",
            "company_name",
            "introduction",
            "vision",
            "pride",
            "address",
            "views",
            "scrap_count",
            "d_day",
        ]

    def get_logo(self, obj):
        if obj.logo:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.logo)
            )

    def get_banner(self, obj):
        if obj.banner:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.banner)
            )

    def get_scrap_count(self, obj):
        return Scrap.objects.filter(board=obj).count()

    def get_d_day(self, obj):
        deadline = obj.created_at + obj.duration
        difference = deadline - timezone.now()
        # 기한이 지난 경우 -1 반환
        return max(difference.days, -1)


class ActivitySerializer(serializers.ModelSerializer):
    period = DurationFieldInISOFormat()

    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
            "kind",
            "people_number",
            "talent",
            "frequency",
            "way",
            "period",
            "recruit",
            "payment",
        ]


class ScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrap
        fields = ["id", "board"]


class FormSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = [
            "id",
            "activity",
            "introduce",
            "reason",
            "merit",
            "accept_status",
        ]


"""
View에 맞게  overriding
GET APIView의 경우 Serializer보다 APIView가 먼저 작동: 필터링 된 모델이 obj로 들어옴.
View에서는 objects(eg. forms)가 반환되었더라도, serialzer에서는 단일 object에 대해 작동.
POST,PUT,DELETE APIView의 경우 APIView가 Serializer보다 먼저 작동.
"""


class BoardListSerializer(BoardSerializer):
    class Meta:
        model = Board
        fields = [
            "id",
            "logo",
            "title",
            "company_name",
            "views",
            "scrap_count",
            "d_day",
        ]


class BoardDetailSerializer(BoardSerializer):
    activity = ActivitySerializer(many=True, read_only=True)

    class Meta:
        model = Board
        fields = [
            "id",
            "logo",
            "banner",
            "title",
            "company_name",
            "introduction",
            "vision",
            "pride",
            "address",
            "views",
            "scrap_count",
            "d_day",
            "activity",
        ]


class BoardCreateSerializer(BoardSerializer):
    activity = ActivitySerializer(many=True)
    logo = serializers.ImageField()
    banner = serializers.ImageField()
    duration = DurationFieldInISOFormat()

    class Meta:
        model = Board
        fields = [
            "logo",
            "banner",
            "title",
            "company_name",
            "introduction",
            "vision",
            "pride",
            "address",
            "duration",
            "activity",
        ]

    def validate_duration(self, value):
        if value < timedelta(days=7) or value > timedelta(days=60):
            raise serializers.ValidationError("모집기간은 7일에서 60일 사이여야 합니다.")
        return value

    def validate_activity(self, activities_data):
        if len(activities_data) > 3:
            raise serializers.ValidationError("대외활동은 최대 3개만 가능합니다.")
        return activities_data

    def validate(self, data):
        if not data.get("title"):
            titles = [activity["title"] for activity in data.get("activity", [])]
            data["title"] = "/".join(titles[:3])
        return data

    @transaction.atomic
    def create(self, validated_data):
        activities_data = validated_data.pop("activity")
        board = Board.objects.create(**validated_data)
        for activity_data in activities_data:
            Activity.objects.create(board=board, **activity_data)
        return board

    # 이미지 반환값을 presigned_url 사용
    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.logo:
            ret["logo"] = generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(instance.logo)
            )
        if instance.banner:
            ret["banner"] = generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(instance.banner)
            )
        return ret


class FormBoardListSerializer(FormSerializer):
    logo = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            "id",
            "accept_status",
            "logo",
            "title",
            "company_name",
        ]

    # obj.board.logo 형태로 사용해야 하므로 BoardSerializer는 상속 불가
    def get_logo(self, obj):
        logo = obj.activity.board.logo
        if logo:
            return generate_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, str(logo))

    def get_title(self, obj):
        return obj.activity.board.title

    def get_company_name(self, obj):
        return obj.activity.board.company_name


class FormBoardDetailSerializer(FormSerializer):
    logo = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    introduction = serializers.SerializerMethodField()
    vision = serializers.SerializerMethodField()
    pride = serializers.SerializerMethodField()
    address = serializers.SerializerMethodField()
    d_day = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            "id",
            "accept_status",
            "logo",
            "banner",
            "title",
            "company_name",
            "introduction",
            "vision",
            "pride",
            "address",
            "d_day",
        ]

    def get_logo(self, obj):
        logo = obj.activity.board.logo
        if logo:
            return generate_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, str(logo))

    def get_banner(self, obj):
        banner = obj.activity.board.banner
        if banner:
            return generate_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, str(banner))

    def get_title(self, obj):
        return obj.activity.board.title

    def get_company_name(self, obj):
        return obj.activity.board.company_name

    def get_introduction(self, obj):
        return obj.activity.board.introduction

    def get_vision(self, obj):
        return obj.activity.board.vision

    def get_pride(self, obj):
        return obj.activity.board.pride

    def get_address(self, obj):
        return obj.activity.board.address

    def get_d_day(self, obj):
        board = obj.activity.board
        deadline = board.created_at + board.duration
        difference = deadline - timezone.now()
        return max(difference.days, -1)


class ActivityListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
        ]


class FormFillSerializer(StudentUserProfileSerializer):
    portfolio_list = StudentUserPortfolioListSerializer(
        source="student_user.student_user_portfolio", many=True
    )
    activity_list = serializers.SerializerMethodField()

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
            "activity_list",
            "portfolio_list",
        ]

    def get_activity_list(self, obj):
        board_id = self.context["view"].kwargs.get("board_id")
        activities = Activity.objects.filter(board__pk=board_id)
        return ActivityListSerializer(activities, many=True).data


class FormCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = [
            "id",
            "activity",
            "introduce",
            "reason",
            "merit",
            "student_user_portfolio",
        ]


class FormDetailSerializer(FormSerializer):
    profile = StudentUserProfileSerializer(source="student_user.student_user_profile")
    activity = ActivityListSerializer()
    student_user_portfolio = StudentUserPortfolioListSerializer()
    activity_list = serializers.SerializerMethodField()

    class Meta:
        model = Form
        fields = [
            "id",
            "activity",
            "introduce",
            "reason",
            "merit",
            "accept_status",
            "profile",
            "student_user_portfolio",
            "activity_list",
            "portfolio_list",
        ]

    def get_activity_list(self, obj):
        board_id = obj.activity.board.pk
        activities = Activity.objects.filter(board__pk=board_id)
        return ActivityListSerializer(activities, many=True).data

    def get_portfolio_list(self, obj):
        user = obj.student_user
        portfolios = StudentUserPortfolio.objects.filter(student_user=user)
        return StudentUserPortfolioListSerializer(portfolios, many=True).data


class CompanyActivityListSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()
    form_count = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
            "deadline",
            "form_count",
        ]

    def get_deadline(self, obj):
        board = obj.board
        deadline = board.created_at + board.duration
        if timezone.now() > deadline:
            return "마감됨"
        return deadline.date()

    def get_form_count(self, obj):
        return Form.objects.filter(activity=obj).count()


class FormListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Form
        fields = [
            "id",
            "accept_status",
        ]


class CompanyActivityFormListSerializer(serializers.ModelSerializer):
    # related_name으로 역방향 쿼리를 추적할 수 있으므로, source를 표기하지 않음
    form = FormListSerializer(many=True, read_only=True)
    name = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
            "name",
            "form",
        ]

    def get_name(self, obj):
        return obj.form.student_user.student_user_profile.name


class CompanyStudentProfileListSerializer(serializers.ModelSerializer):
    portfolio_list = StudentUserPortfolioListSerializer(
        source="student_user.student_user_portfolio", many=True
    )

    class Meta:
        model = StudentUserProfile
        fields = [
            "id",
            "name",
            "university",
            "major",
            "portfolio_list",
        ]


class CompanyStudentProfileDetailSerializer(serializers.ModelSerializer):
    portfolio_list = StudentUserPortfolioListSerializer(
        source="student_user.student_user_portfolio", many=True
    )
    profile_image = serializers.SerializerMethodField()

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
            "portfolio_list",
        ]

    def get_profile_image(self, obj):
        if obj.profile_image:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.profile_image)
            )


class CompanyStudentPortfolioDetailSerializer(serializers.ModelSerializer):
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


class SuggestionSerializer(serializers.ModelSerializer):
    class Meta:
        model = Suggestion
        fields = [
            "id",
            "company_user",
            "student_user",
        ]


class SuggestionListSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()

    class Meta:
        model = Suggestion
        fields = [
            "id",
            "company_name",
        ]

    def get_company_name(self, obj):
        board = obj.company_user.board.first()
        return board.company_name
