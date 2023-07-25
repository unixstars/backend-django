from django.conf import settings
from rest_framework import serializers
from .models import Board, Activity, Scrap
from api.utils import generate_presigned_url
from api.serializers import DurationFieldInISOFormat
from django.utils import timezone
from django.db import transaction


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


class BoardListSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    scrap_count = serializers.SerializerMethodField()
    d_day = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "id",
            "logo",
            "title",
            "company_name",
            "is_expired",
            "views",
            "scrap_count",
            "d_day",
        ]

    def get_logo(self, obj):
        if obj.logo:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.logo)
            )

    def get_title(self, obj):
        # title이 None인 경우에 대한 처리
        if obj.title is None and obj.activity:
            # activity의 title을 최대 3개까지 가져와서 '/'로 이어줍니다.
            activity_titles = [activity.title for activity in obj.activity.all()[:3]]
            return "/".join(activity_titles)
        return obj.title

    def get_scrap_count(self, obj):
        return Scrap.objects.filter(board=obj).count()

    def get_d_day(self, obj):
        obj.update_expired_status()
        deadline = obj.created_at + obj.duration
        difference = deadline - timezone.now()
        # d-day 또는 기한이 지난 경우 0 반환
        return max(difference.days, 0)


class BoardDetailSerializer(BoardListSerializer):
    activity = ActivitySerializer(many=True, read_only=True)
    banner = serializers.SerializerMethodField()

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
            "is_expired",
            "views",
            "scrap_count",
            "d_day",
            "activity",
        ]

    def get_banner(self, obj):
        if obj.banner:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.banner)
            )


class BoardCreateSerializer(serializers.ModelSerializer):
    activity = ActivitySerializer(many=True)
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

    def validate_activity(self, activities_data):
        if len(activities_data) > 3:
            raise serializers.ValidationError("대외활동은 최대 3개만 가능합니다.")
        return activities_data

    @transaction.atomic
    def create(self, validated_data):
        activities_data = validated_data.pop("activity")
        board = Board.objects.create(**validated_data)
        for activity_data in activities_data:
            Activity.objects.create(board=board, **activity_data)
        return board


class ScrapSerializer(serializers.ModelSerializer):
    class Meta:
        model = Scrap
        fields = ["id", "board", "student_user"]
