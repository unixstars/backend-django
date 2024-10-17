from django.db import models
from activity.models import Activity, Form
from django.utils import timezone


class AcceptedApplicant(models.Model):
    ONGOING, CANCELED, COMPLETED = "ongoing", "canceled", "completed"
    ACTIVITY_STATUS_CHOICES = (
        (ONGOING, "진행중"),
        (CANCELED, "취소"),
        (COMPLETED, "완료"),
    )

    form = models.OneToOneField(
        Form, on_delete=models.CASCADE, related_name="accepted_applicant"
    )
    start_date = models.DateField(default=timezone.now)
    week = models.IntegerField(default=1)
    activity_status = models.CharField(
        max_length=10,
        choices=ACTIVITY_STATUS_CHOICES,
        default=ONGOING,
    )

    def __str__(self):
        return f"{self.form} 합격자"


class ApplicantWarning(models.Model):
    accepted_applicant = models.ForeignKey(
        AcceptedApplicant, on_delete=models.CASCADE, related_name="applicant_warning"
    )
    content = models.CharField(max_length=50, default="")

    def __str__(self) -> str:
        return f"{self.accepted_applicant} 경고"


class Notice(models.Model):

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="notice",
    )

    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.activity} 공지:{self.title}"


class Assignment(models.Model):

    activity = models.ForeignKey(
        Activity,
        on_delete=models.CASCADE,
        related_name="assignment",
    )

    title = models.CharField(max_length=100)  # 프론트(실제) 글자제한 30
    content = models.TextField()
    duration = models.DurationField()
    duration_extended = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.activity} 과제:{self.title}"


class Submit(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="submit"
    )

    accepted_applicant = models.ForeignKey(
        AcceptedApplicant,
        on_delete=models.CASCADE,
        related_name="submit",
    )

    IN_PROGRESS, FIRST_REVISION, SECOND_REVISION, FINAL_APPROVAL = (
        "in_progress",
        "first_revision",
        "second_revision",
        "final_approval",
    )
    PROGRESS_STATUS_CHOICES = (
        (IN_PROGRESS, "진행중"),
        (FIRST_REVISION, "1차수정"),
        (SECOND_REVISION, "2차수정"),
        (FINAL_APPROVAL, "최종승인"),
    )

    content = models.TextField(null=True, blank=True)
    progress_status = models.CharField(
        max_length=30,
        choices=PROGRESS_STATUS_CHOICES,
        default=IN_PROGRESS,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    class Meta:
        unique_together = [
            "assignment",
            "accepted_applicant",
        ]

    def __str__(self) -> str:
        return f"{self.assignment} 제출물"


class SubmitFile(models.Model):
    def get_upload_path_file(instance, filename):
        return "activity/{}/student/{}/assginment/{}".format(
            instance.submit.assignment.activity.pk,
            instance.submit.accepted_applicant.form.student_user.pk,
            filename,
        )

    submit = models.ForeignKey(
        Submit, on_delete=models.CASCADE, related_name="submit_file"
    )

    file = models.FileField(
        upload_to=get_upload_path_file,
        max_length=200,
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.submit} 파일:{self.file}"


class AcceptedChatRoom(models.Model):
    accepted_applicant = models.ForeignKey(
        AcceptedApplicant, on_delete=models.CASCADE, related_name="accepted_chatroom"
    )
    title = models.CharField(max_length=30)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.accepted_applicant}의 채팅방"


class AcceptedMessage(models.Model):
    accepted_chatroom = models.ForeignKey(
        AcceptedChatRoom, on_delete=models.CASCADE, related_name="accepted_message"
    )
    author_id = models.IntegerField()
    author_name = models.CharField(max_length=30)
    author_logo = models.URLField(max_length=300)
    content = models.TextField()
    STUDENT, COMPANY = "student", "company"
    USER_TYPE_CHOICES = [
        (STUDENT, "학생유저"),
        (COMPANY, "기업유저"),
    ]
    user_type = models.CharField(
        max_length=30, choices=USER_TYPE_CHOICES, default=STUDENT
    )
    is_read = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.accepted_chatroom} 채팅방 메시지"
