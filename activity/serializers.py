from django.conf import settings
from rest_framework import serializers
from .models import Board, Activity, Scrap
from api.views import generate_presigned_url
from api.serializers import DurationFieldInISOFormat


class ActivitySerializer(serializers.ModelSerializer):
    period = DurationFieldInISOFormat()

    class Meta:
        model = Activity
        fields = [
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


class BoardSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    duration = DurationFieldInISOFormat()
    scrap_count = serializers.SerializerMethodField()
    activity = ActivitySerializer(many=True, read_only=True)

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
            "is_expired",
            "views",
            "scrap_count",
            "created_at",
            "activity",
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

    def get_title(self, obj):
        # title이 None인 경우에 대한 처리
        if obj.title is None and obj.activity:
            # activity의 title을 최대 3개까지 가져와서 '/'로 이어줍니다.
            activity_titles = [activity.title for activity in obj.activity.all()[:3]]
            return "/".join(activity_titles)
        return obj.title

    def get_scrap_count(self, obj):
        return Scrap.objects.filter(board=obj).count()
