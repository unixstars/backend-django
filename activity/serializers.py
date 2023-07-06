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
    activities = ActivitySerializer(many=True, read_only=True)
    scrap_count = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()
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
            "is_expired",
            "views",
            "created_at",
            "scrap_count",
            "activities",
        ]

    def get_scrap_count(self, obj):
        return Scrap.objects.filter(board=obj).count()

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
