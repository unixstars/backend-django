from django.conf import settings
from rest_framework import serializers
from .models import Board, Activity, Scrap, Form
from api.utils import generate_presigned_url
from api.serializers import DurationFieldInISOFormat
from django.utils import timezone
from django.db import transaction
from datetime import timedelta


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
        # d-day 또는 기한이 지난 경우 0 반환
        return max(difference.days, 0)


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

    """
    ListAPIView(GET)의 경우 Serializer보다 APIView가 먼저 작동하므로, 필터링 된 form이 obj로 들어옴.
    View에서는 forms가 반환되었더라도, serialzer에서는 단일 form에 대해 작동. obj = 단일 form 객체
    """

    def get_logo(self, obj):
        board = obj.activity.board
        if board.logo:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(board.logo)
            )

    def get_title(self, obj):
        board = obj.activity.board
        title = board.title
        return title

    def get_company_name(self, obj):
        board = obj.activity.board
        company_name = board.company_name
        return company_name
