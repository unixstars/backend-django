from rest_framework import serializers
from django.conf import settings
from .models import (
    AcceptedApplicant,
    ApplicantWarning,
    Notice,
    Assignment,
    Submit,
    SubmitFile,
    AcceptedChatRoom,
    AcceptedMessage,
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


class NoticeDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = Notice
        fields = [
            "id",
            "title",
            "content",
            "created_at",
        ]


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
        queryset=AcceptedApplicant.objects.all(),
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


class CompanyProgramAssignmentDetailSerializer(serializers.ModelSerializer):
    deadline = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            "id",
            "title",
            "content",
            "deadline",
            "created_at",
            "updated_at",
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


class CompanyProgramAssignmentSubmitNameListSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()

    class Meta:
        model = Submit
        fields = ["id", "name"]

    def get_name(self, obj):
        name = obj.accepted_applicant.form.student_user.student_user_profile.name
        return name


class CompanyProgramAssignmentSubmitListSerializer(serializers.ModelSerializer):
    activity_title = serializers.SerializerMethodField()
    company_name = serializers.SerializerMethodField()
    week = serializers.SerializerMethodField()
    total_week = serializers.SerializerMethodField()
    submits = serializers.SerializerMethodField()

    class Meta:
        model = Assignment
        fields = [
            "title",
            "activity_title",
            "company_name",
            "week",
            "total_week",
            "submits",
        ]

    def get_activity_title(self, obj):
        return obj.activity.title

    def get_company_name(self, obj):
        return obj.activity.board.company_name

    def get_week(self, obj):
        form = obj.activity.form.first()
        week = form.accepted_applicant.week
        return week

    def get_total_week(self, obj):
        period = obj.activity.period
        weeks, remaining_days = divmod(period.days, 7)
        if remaining_days > 0:
            weeks += 1
        return weeks

    def get_submits(self, obj):
        submits = Submit.objects.filter(assignment=obj).select_related(
            "accepted_applicant__form__student_user__student_user_profile"
        )
        return CompanyProgramAssignmentSubmitNameListSerializer(submits, many=True).data


class CompanyProgramAssignmentSubmitDetailSerializer(serializers.ModelSerializer):
    name = serializers.SerializerMethodField()
    title = serializers.SerializerMethodField()
    submit_file = SubmitFileSerializer(many=True)

    class Meta:
        model = Submit
        fields = [
            "id",
            "name",
            "title",
            "content",
            "progress_status",
            "submit_file",
        ]

    def get_name(self, obj):
        name = obj.accepted_applicant.form.student_user.student_user_profile.name
        return name

    def get_title(self, obj):
        title = obj.assignment.title
        return title


class AcceptedMessageSerializer(serializers.ModelSerializer):
    author_logo = serializers.SerializerMethodField()

    class Meta:
        model = AcceptedMessage
        fields = [
            "id",
            "author_id",
            "author_name",
            "author_logo",
            "content",
            "user_type",
            "is_read",
            "created_at",
        ]
        read_only_fields = [
            "author_id",
            "author_name",
            "author_logo",
            "user_type",
            "is_read",
            "created_at",
        ]

    def get_author_logo(self, obj):
        if obj.author_logo:
            return f"{settings.MEDIA_URL}{obj.author_logo}"
        return None


class AcceptedChatRoomSerializer(serializers.ModelSerializer):
    last_message = serializers.SerializerMethodField()
    non_read = serializers.SerializerMethodField()

    class Meta:
        model = AcceptedChatRoom
        fields = [
            "id",
            "title",
            "participants",
            "last_message",
            "non_read",
        ]

    def get_participants(self, obj):
        accepted_applicant_exists = AcceptedApplicant.objects.filter(
            form__activity=obj.activity
        ).exists()
        if accepted_applicant_exists:
            return (
                AcceptedApplicant.objects.filter(form__activity=obj.activity).count()
                + 1
            )
        else:
            return 1

    def get_last_message(self, obj):
        last_message = obj.accepted_message.order_by("-created_at").first()
        if last_message:
            return AcceptedMessageSerializer(last_message).data
        return None

    def get_non_read(self, obj):
        if AcceptedMessage.objects.filter(accepted_chatroom=obj).exists():
            return (
                AcceptedMessage.objects.filter(accepted_chatroom=obj)
                .filter(is_read=False)
                .count()
            )
        else:
            return 0
