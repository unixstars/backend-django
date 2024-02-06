from django.db import models
from activity.models import Form
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
    content = models.CharField(max_length=50)

    def __str__(self) -> str:
        return f"{self.accepted_applicant} 경고"


class Notice(models.Model):
    accepted_applicant = models.ForeignKey(
        AcceptedApplicant, on_delete=models.CASCADE, related_name="notice"
    )

    title = models.CharField(max_length=30)
    content = models.TextField()
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.accepted_applicant} 공지:{self.title}"


class NoticeComment(models.Model):
    notice = models.ForeignKey(
        Notice, on_delete=models.CASCADE, related_name="notice_comment"
    )

    STUDENT, COMPANY = "student", "company"
    USER_TYPE_CHOICES = (
        (STUDENT, "학생유저"),
        (COMPANY, "기업유저"),
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default=STUDENT
    )

    def __str__(self) -> str:
        return f"{self.notice} 댓글"


class Assignment(models.Model):
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

    accepted_applicant = models.ForeignKey(
        AcceptedApplicant, on_delete=models.CASCADE, related_name="assignment"
    )

    title = models.CharField(max_length=30)
    content = models.TextField()
    progress_status = models.CharField(
        max_length=30,
        choices=PROGRESS_STATUS_CHOICES,
        default=IN_PROGRESS,
    )
    duration = models.DurationField()
    duration_extended = models.IntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.accepted_applicant} 과제:{self.title}"


class AssignmentComment(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="assignment_comment"
    )

    STUDENT, COMPANY = "student", "company"
    USER_TYPE_CHOICES = (
        (STUDENT, "학생유저"),
        (COMPANY, "기업유저"),
    )
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default=STUDENT
    )

    def __str__(self) -> str:
        return f"{self.assignment} 댓글"


class Submit(models.Model):
    assignment = models.OneToOneField(
        Assignment, on_delete=models.CASCADE, related_name="submit"
    )

    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.assignment} 제출물"


class SubmitFile(models.Model):
    def get_upload_path_file(instance, filename):
        return "activity/{}/student/{}/assginment/{}".format(
            instance.submit.assignment.accepted_applicant.form.activity.pk,
            instance.submit.assignment.accepted_applicant.form.student_user.pk,
            filename,
        )

    submit = models.ForeignKey(
        Submit, on_delete=models.CASCADE, related_name="submit_file"
    )

    file = models.FileField(upload_to=get_upload_path_file)
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.submit} 파일:{self.file}"
