from rest_framework import serializers
from rest_framework.exceptions import ValidationError
from django.conf import settings
from .models import (
    AcceptedApplicant,
    ApplicantWarning,
    ApplicantComment,
    Notice,
    NoticeComment,
    Assignment,
    AssignmentComment,
    Submit,
    SubmitFile,
)
from activity.models import Activity, Form
from api.serializers import DurationFieldInISOFormat


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
            return f"{settings.MEDIA_URL}{logo}"

    def get_company_name(self, obj):
        company_name = obj.form.activity.board.company_name
        return company_name

    def get_total_week(self, obj):
        period = obj.form.activity.period
        weeks, remaining_days = divmod(period.days, 7)
        if remaining_days > 0:
            weeks += 1
        return weeks


class NoticeListSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "created_at",
        ]


class AssignmentListSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "deadline",
            "created_at",
            "updated_at",
        ]

    def get_deadline(self, obj):
        deadline_datetime = obj.created_at + obj.duration
        deadline_date = deadline_datetime.date()
        return deadline_date


class ProgramDetailSerializer(serializers.ModelSerializer):
    activity_title = serializers.SerializerMethodField()
    logo = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    total_week = serializers.SerializerMethodField()
    warning_count = serializers.SerializerMethodField()
    notice = serializers.SerializerMethodField()
    assignment = serializers.SerializerMethodField()

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
            return f"{settings.MEDIA_URL}{logo}"

    def get_company_name(self, obj):
        company_name = obj.form.activity.board.company_name
        return company_name

    def get_total_week(self, obj):
        period = obj.form.activity.period
        weeks, remaining_days = divmod(period.days, 7)
        if remaining_days > 0:
            weeks += 1
        return weeks

    def get_warning_count(self, obj) -> int:
        warnings = ApplicantWarning.objects.filter(accepted_applicant=obj)
        return warnings.count()

    def get_notice(self, obj):
        notices = obj.form.activity.notice.all()
        return NoticeListSerializer(notices, many=True).data

    def get_assignment(self, obj):
        assignments = obj.form.activity.assignment.all()
        return AssignmentListSerializer(assignments, many=True).data


class ProgramWarningSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantWarning
        fields = ["id", "content"]


class ApplicantCommentListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    image = serializers.SerializerMethodField()
    is_myself = serializers.SerializerMethodField()

    class Meta:
        model = ApplicantComment
        fields = [
            "name",
            "image",
            "content",
            "user_type",
            "is_myself",
            "created_at",
        ]

    def get_name(self, obj):
        user_type = obj.user_type
        if user_type == ApplicantComment.STUDENT:
            name = obj.accepted_applicant.form.student_user.student_user_profile.name
            return name
        else:
            return obj.activity.board.company_name

    def get_image(self, obj):
        user_type = obj.user_type
        if user_type == ApplicantComment.STUDENT:
            image = (
                obj.accepted_applicant.form.student_user.student_user_profile.profile_image
            )
            if image:
                return f"{settings.MEDIA_URL}{image}"
        else:
            image = obj.activity.board.logo
            if image:
                return f"{settings.MEDIA_URL}{image}"

    def get_is_myself(self, obj):
        request = self.context.get("request")

        # 학생 사용자가 댓글의 작성자인지 확인
        if hasattr(request.user, "student_user"):
            return (
                obj.user_type == ApplicantComment.STUDENT
                and request.user.student_user
                == obj.accepted_applicant.form.student_user
            )

        # 기업 사용자가 댓글의 작성자인지 확인
        elif hasattr(request.user, "company_user"):
            return (
                obj.user_type == ApplicantComment.COMPANY
                and request.user.company_user == obj.activity.board.company_user
            )

        return False


class ApplicantCommentCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = ApplicantComment
        fields = ["content"]


class NoticeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "content",
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
        return f"{settings.MEDIA_URL}{image}"


class NoticeCommentCreateSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = NoticeComment
        fields = [
            "image",
            "content",
            "user_type",
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
        return f"{settings.MEDIA_URL}{image}"


class SubmitFileSerializer(serializers.ModelSerializer):
    id = serializers.IntegerField(required=False)

    class Meta:
        model = SubmitFile
        fields = [
            "id",
            "file",
        ]

    def get_file(self, obj):
        if obj.file:
            return f"{settings.MEDIA_URL}{obj.file}"

    def to_representation(self, instance):
        ret = super().to_representation(instance)
        if instance.file:
            ret["file"] = f"{settings.MEDIA_URL}{instance.file}"
        return ret


class SubmitSerializer(serializers.ModelSerializer):
    submit_file = SubmitFileSerializer(many=True)

    class Meta:
        model = Submit
        fields = [
            "id",
            "content",
            "progress_status",
            "submit_file",
        ]


class AssignmentDetailSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()
    submit = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "content",
            "deadline",
            "created_at",
            "submit",
        ]

    def get_deadline(self, obj):
        deadline_datetime = obj.created_at + obj.duration
        deadline_date = deadline_datetime.date()
        return deadline_date

    def get_submit(self, obj):
        assignment_id = self.context.get("assignment_id")
        program_id = self.context.get("program_id")
        submits = Submit.objects.filter(
            accepted_applicant__pk=program_id, assignment__pk=assignment_id
        )
        if submits.exists():
            return SubmitSerializer(submits.first()).data
        else:
            return {}


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
        return f"{settings.MEDIA_URL}{image}"


class AssignmentCommentCreateSerializer(serializers.ModelSerializer):
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
        return f"{settings.MEDIA_URL}{image}"


class SubmitCreateSerializer(serializers.ModelSerializer):
    submit_file = SubmitFileSerializer(many=True, required=False)

    class Meta:
        model = Submit
        fields = [
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


class OtherSubmitListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = Submit
        fields = [
            "id",
            "name",
            "title",
            "progress_status",
            "created_at",
            "updated_at",
        ]

    def get_name(self, obj):
        name = obj.accepted_applicant.form.student_user.student_user_profile.name
        return name

    def get_title(self, obj):
        title = obj.assignment.title
        return title


class OtherSubmitDetailSerializer(serializers.ModelSerializer):
    submit_file = SubmitFileSerializer(many=True)
    name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()

    class Meta:
        model = Submit
        fields = [
            "name",
            "title",
            "content",
            "progress_status",
            "submit_file",
            "created_at",
            "updated_at",
        ]

    def get_name(self, obj):
        name = obj.accepted_applicant.form.student_user.student_user_profile.name
        return name

    def get_title(self, obj):
        title = obj.assignment.title
        return title


##########################################################################################################################


class CompanyProgramListSerializer(serializers.ModelSerializer):
    logo = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    total_week = serializers.SerializerMethodField()
    activity_status = serializers.SerializerMethodField()

    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
            "logo",
            "company_name",
            "week",
            "total_week",
            "activity_status",
        ]

    def get_logo(self, obj):
        logo = obj.board.logo
        if logo:
            return f"{settings.MEDIA_URL}{logo}"

    def get_company_name(self, obj):
        company_name = obj.board.company_name
        return company_name

    def get_week(self, obj):
        first_form = obj.form.filter(accept_status=Form.ACCEPTED).first()
        return first_form.accepted_applicant.week

    def get_total_week(self, obj):
        period = obj.period
        weeks, remaining_days = divmod(period.days, 7)
        if remaining_days > 0:
            weeks += 1
        return weeks

    def get_activity_status(self, obj):
        first_form = obj.form.filter(accept_status=Form.ACCEPTED).first()
        return first_form.accepted_applicant.activity_status


class CompanyProgramApplicantSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    warning_count = serializers.SerializerMethodField()

    class Meta:
        model = AcceptedApplicant
        fields = [
            "id",
            "student_name",
            "warning_count",
        ]

    def get_student_name(self, obj):
        return obj.form.student_user.student_user_profile.name

    def get_warning_count(self, obj) -> int:
        warnings = obj.applicant_warning.all()
        return warnings.count()


class CompanyProgramDetailSerializer(serializers.ModelSerializer):
    company_name = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    total_week = serializers.SerializerMethodField()
    activity_status = serializers.SerializerMethodField()
    notice = NoticeListSerializer(many=True)
    assignment = AssignmentListSerializer(many=True)

    class Meta:
        model = Activity
        fields = [
            "id",
            "title",
            "company_name",
            "week",
            "total_week",
            "activity_status",
            "notice",
            "assignment",
        ]

    def get_company_name(self, obj):
        company_name = obj.board.company_name
        return company_name

    def get_week(self, obj):
        form = obj.form.first()
        week = form.accepted_applicant.week
        return week

    def get_total_week(self, obj):
        period = obj.period
        weeks, remaining_days = divmod(period.days, 7)
        if remaining_days > 0:
            weeks += 1
        return weeks

    def get_activity_status(self, obj):
        form = obj.form.first()
        activity_status = form.accepted_applicant.activity_status
        return activity_status


class CompanyProgramWarningSerializer(serializers.ModelSerializer):
    student_name = serializers.SerializerMethodField()
    warning_count = serializers.SerializerMethodField()

    class Meta:
        model = AcceptedApplicant
        fields = [
            "id",
            "student_name",
            "warning_count",
        ]

    def get_student_name(self, obj):
        return obj.form.student_user.student_user_profile.name

    def get_warning_count(self, obj) -> int:
        warnings = obj.applicant_warning.all()
        return warnings.count()


class CompanyProgramWarningCreateSerializer(serializers.ModelSerializer):
    applicant_id = serializers.PrimaryKeyRelatedField(
        queryset=ApplicantWarning.objects.all(),
        source="accepted_applicant",
        write_only=True,
    )

    class Meta:
        model = ApplicantWarning
        fields = ["applicant_id"]


class CompanyProgramNoticeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "content",
            "is_checked",
            "created_at",
        ]


class CompanyProgramNoticeCreateSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "content",
        ]


class CompanyProgramNoticeCommentCreateSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = NoticeComment
        fields = [
            "image",
            "content",
            "user_type",
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
        return f"{settings.MEDIA_URL}{image}"


class CompanyProgramAssignmentDetailSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()
    submit = SubmitSerializer()

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "content",
            "deadline",
            "created_at",
            "submit",
        ]

    def get_deadline(self, obj):
        deadline_datetime = obj.created_at + obj.duration
        deadline_date = deadline_datetime.date()
        return deadline_date


class CompanyProgramAssignmentCreateSerializer(serializers.ModelSerializer):
    duration = DurationFieldInISOFormat()

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "content",
            "duration",
        ]


class CompanyProgramAssignmentCommentCreateSerializer(serializers.ModelSerializer):
    image = serializers.SerializerMethodField()

    class Meta:
        model = AssignmentComment
        fields = [
            "image",
            "content",
            "user_type",
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
        return f"{settings.MEDIA_URL}{image}"
