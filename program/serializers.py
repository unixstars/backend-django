from rest_framework import serializers
from django.conf import settings
from api.utils import generate_presigned_url
from .models import (
    AcceptedApplicant,
    ApplicantWarning,
    Notice,
    NoticeComment,
    Assignment,
    AssignmentComment,
    Submit,
    SubmitFile,
)


class ProgramListSerializer(serializers.ModelSerializer):
    activity_title = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    total_week = serializers.SerializerMethodField()

    class Meta:
        model = AcceptedApplicant
        fields = [
            "id",
            "activity_title",
            "logo",
            "company_name",
            "week",
            "total_week",
            "activity_status",
        ]

    def get_activity_title(self, obj):
        activity_title = obj.form.activity.title
        return activity_title

    def get_logo(self, obj):
        logo = obj.form.activity.board.logo
        if logo:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME,
                str(logo),
            )

    def get_company_name(self, obj):
        company_name = obj.form.activity.board.company_name
        return company_name

    def get_total_week(self, obj):
        duration = obj.form.activity.board.duration
        weeks, remaining_days = divmod(duration.days, 7)
        if remaining_days > 0:
            weeks += 1
        return weeks


class NoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "is_checked",
            "created_at",
        ]


class AssignmentListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "progress_status",
        ]


class ProgramDetailSerializer(serializers.ModelSerializer):
    activity_title = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    total_week = serializers.SerializerMethodField()
    warning_count = serializers.SerializerMethodField()
    notice = NoticeListSerializer(many=True)
    assignment = AssignmentListSerializer(many=True)

    class Meta:
        model = AcceptedApplicant
        fields = [
            "id",
            "activity_title",
            "logo",
            "company_name",
            "week",
            "total_week",
            "activity_status",
            "warning_count",
            "notice",
            "assignment",
        ]

    def get_activity_title(self, obj):
        activity_title = obj.form.activity.title
        return activity_title

    def get_logo(self, obj):
        logo = obj.form.activity.board.logo
        if logo:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME,
                str(logo),
            )

    def get_company_name(self, obj):
        company_name = obj.form.activity.board.company_name
        return company_name

    def get_total_week(self, obj):
        duration = obj.form.activity.board.duration
        weeks, remaining_days = divmod(duration.days, 7)
        if remaining_days > 0:
            weeks += 1
        return weeks

    def get_warning_count(self, obj) -> int:
        warnings = ApplicantWarning.objects.filter(accepted_applicant=obj)
        if not warnings:
            return 0
        return warnings.count()


class ProgramWarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantWarning
        fields = ["id", "content"]


class NoticeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "content",
            "is_checked",
            "created_at",
        ]


class NoticeCommentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = NoticeComment
        fields = [
            "user_type",
            "image",
            "content",
            "created_at",
        ]

    def get_image(self, obj):
        user_type = obj.user_type
        if user_type == NoticeComment.STUDENT:
            image = (
                obj.notice.accepted_applicant.form.student_user.student_user_profile.profile_image
            )
        else:
            image = obj.notice.accepted_applicant.form.activity.board.logo
        return generate_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, str(image))


class NoticeCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = NoticeComment
        fields = ["content"]


class SubmitFileSerializer(serializers.ModelSerializer):
    file = serializers.SerializerMethodField()

    class Meta:
        model = SubmitFile
        fields = [
            "id",
            "file",
        ]

    def get_file(self, obj):
        if obj.file:
            return generate_presigned_url(
                settings.AWS_STORAGE_BUCKET_NAME, str(obj.file)
            )


class SubmitSerializer(serializers.ModelSerializer):
    submit_file = SubmitFileSerializer(many=True)

    class Meta:
        model = Submit
        fields = [
            "id",
            "content",
            "submit_file",
        ]


class AssignmentDetailSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()
    submit = SubmitSerializer()

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "progress_status",
            "deadline",
            "created_at",
            "submit",
        ]

    def get_deadline(self, obj):
        deadline_datetime = obj.created_at + obj.duration
        deadline_date = deadline_datetime.date()
        return deadline_date


class AssignmentCommentSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentComment
        fields = [
            "user_type",
            "image",
            "content",
            "created_at",
        ]

    def get_image(self, obj):
        user_type = obj.user_type
        if user_type == AssignmentComment.STUDENT:
            image = (
                obj.assignment.accepted_applicant.form.student_user.student_user_profile.profile_image
            )
        else:
            image = obj.assignment.accepted_applicant.form.activity.board.logo
        return generate_presigned_url(settings.AWS_STORAGE_BUCKET_NAME, str(image))


class AssignmentCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = AssignmentComment
        fields = ["content"]


class SubmitCreateSerializer(serializers.ModelSerializer):
    submit_file = SubmitFileSerializer(many=True, required=False)

    class Meta:
        model = Submit
        fields = [
            "id",
            "content",
            "submit_file",
        ]

    def create(self, validated_data):
        submit_files_data = validated_data.pop("submit_file", [])
        submit = Submit.objects.create(**validated_data)
        for file_data in submit_files_data:
            SubmitFile.objects.create(submit=submit, **file_data)

        return submit


class SubmitUpdateSerializer(serializers.ModelSerializer):
    submit_file = SubmitFileSerializer(many=True, required=False)

    class Meta:
        model = Submit
        fields = [
            "id",
            "content",
            "submit_file",
        ]

    def update(self, instance, validated_data):
        # 유효성 검사가 끝난 데이터에서 submit_file 데이터 추출(), 데이터가 없으면 빈 객체 반환
        submit_files_data = validated_data.pop("submit_file", [])

        # 클라이언트에서 유저가 수정하는 특정 파일의 id를 보내줘야 함.
        for file_data in submit_files_data:
            file_id = file_data.get("id", None)
            if file_id:  # 기존에 있던 파일을 수정하려는 경우
                file_instance = SubmitFile.objects.get(id=file_id)
                for attr, value in file_data.items():
                    setattr(file_instance, attr, value)
                file_instance.save()
            else:  # 새로운 파일을 추가하려는 경우
                SubmitFile.objects.create(submit=instance, **file_data)

        instance.content = validated_data.get("content", instance.content)
        # 업데이트 된 submit 인스턴스 저장
        instance.save()

        return instance
