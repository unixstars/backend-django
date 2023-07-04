from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError


class Board(models.Model):
    def get_upload_path_logo(instance, filename):
        return "company/{}/logo/{}".format(
            instance.company_user_id.pk,
            filename,
        )

    def get_upload_path_banner(instance, filename):
        return "company/{}/banner/{}".format(
            instance.company_user_id.pk,
            filename,
        )

    board_id = models.AutoField(primary_key=True)
    company_user_id = models.ForeignKey("user.CompanyUser", on_delete=models.CASCADE)
    company_name = models.CharField(max_length=30)
    logo = models.ImageField(
        upload_to=get_upload_path_logo,
        null=True,
        blank=True,
    )
    banner = models.ImageField(
        upload_to=get_upload_path_banner,
        null=True,
        blank=True,
    )
    title = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )
    company_name = models.CharField(max_length=30)
    introduction = models.TextField()
    vision = models.TextField()
    pride = models.CharField(
        max_length=200,
        null=True,
        blank=True,
    )
    address = models.CharField(max_length=150)
    duration = models.DurationField()
    is_expired = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)
    views = models.PositiveIntegerField(default=0)

    def clean(self):
        if self.duration < timedelta(days=7) or self.duration > timedelta(days=365):
            raise ValidationError("모집기간은 7과 365사이여야 합니다.")


class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)

    title = models.CharField(max_length=20)
    kind = models.CharField(max_length=20)
    people_number = models.IntegerField()
    talent = models.TextField()
    frequency = models.TextField()
    way = models.TextField()
    period = models.DurationField()
    recruit = models.BooleanField(default=False)
    payment = models.CharField(
        max_length=20,
        null=True,
        blank=True,
    )


class Scrap(models.Model):
    scrap_id = models.AutoField(primary_key=True)
    student_user_id = models.ForeignKey("user.StudentUser", on_delete=models.CASCADE)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)


class Form(models.Model):
    PENDING, WAITING, CANCELED, REJECTED, ACCEPTED = (
        "pending",
        "waiting",
        "canceled",
        "rejected",
        "accepted",
    )

    IS_ACCEPTED_CHOICES = [
        (PENDING, "대기중"),
        (WAITING, "확정대기"),
        (CANCELED, "활동취소"),
        (REJECTED, "불합격"),
        (ACCEPTED, "합격"),
    ]

    form_id = models.AutoField(primary_key=True)
    introduce = models.TextField(default="")
    reason = models.TextField(default="")
    merit = models.TextField(default="")
    is_accepted = models.CharField(
        max_length=10,
        choices=IS_ACCEPTED_CHOICES,
        default=PENDING,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
    activity_id = models.ForeignKey(Activity, on_delete=models.CASCADE)
    student_user_id = models.ForeignKey("user.StudentUser", on_delete=models.CASCADE)
