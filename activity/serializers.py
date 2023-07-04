from django.conf import settings
from rest_framework import serializers
from .models import Board, Activity, Scrap
from api.views import generate_presigned_url


class ActivitySerializer(serializers.ModelSerializer):
    class Meta:
        model = Activity
        fields = "__all__"


class BoardSerializer(serializers.ModelSerializer):
    activities = ActivitySerializer(source="board_id", many=True, read_only=True)
    scrap_count = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    banner = serializers.SerializerMethodField()

    class Meta:
        model = Board
        fields = [
            "company_user_id",
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
            "logo",
            "banner",
            "scrap_count",
            "activities",
        ]

    def get_scrap_count(self, obj):
        return Scrap.objects.filter(board_id=obj).count()

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
