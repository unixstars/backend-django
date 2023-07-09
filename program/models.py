from django.core.validators import MinValueValidator, MaxValueValidator
from django.db import models
from activity.models import Form


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
    warning = models.IntegerField(
        default=0, validators=[MinValueValidator(0), MaxValueValidator(5)]
    )
    start_date = models.DateField()
    week = models.PositiveIntegerField(default=1)
    activity_status = models.CharField(
        max_length=10,
        choices=ACTIVITY_STATUS_CHOICES,
        default=ONGOING,
    )


class Notice(models.Model):
    accepted_applicant = models.ForeignKey(
        AcceptedApplicant, on_delete=models.CASCADE, related_name="notice"
    )

    title = models.CharField(max_length=30)
    content = models.TextField()
    is_checked = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)


class NoticeComment(models.Model):
    notice = models.ForeignKey(
        Notice, on_delete=models.CASCADE, related_name="notice_comment"
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


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


class AssignmentComment(models.Model):
    assignment = models.ForeignKey(
        Assignment, on_delete=models.CASCADE, related_name="assignment_comment"
    )

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)


class Submit(models.Model):
    assignment = models.OneToOneField(
        Assignment, on_delete=models.CASCADE, related_name="submit"
    )

    content = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SubmitFiles(models.Model):
    submit = models.OneToOneField(
        Submit, on_delete=models.CASCADE, related_name="submit_files"
    )


class SubmitOneFile(models.Model):
    def get_upload_path_file(instance, filename):
        return "activity/{}/student/{}/assginment/{}".format(
            instance.submitfiles.submit.assignment.accepted_applicant.form.activity.pk,
            instance.submitfiles.submit.assignment.accepted_applicant.form.student.pk,
            filename,
        )

    submitfiles = models.ForeignKey(
        SubmitFiles, on_delete=models.CASCADE, related_name="submit_one_file"
    )

    file = models.FileField(upload_to=get_upload_path_file)
