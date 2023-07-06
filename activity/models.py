from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError
from PIL import Image
import io
import boto3
from django.conf import settings
import urllib.request


class Board(models.Model):
    def get_upload_path_logo(instance, filename):
        return "company/{}/logo/{}".format(
            instance.company_user.pk,
            filename,
        )

    def get_upload_path_banner(instance, filename):
        return "company/{}/banner/{}".format(
            instance.company_user.pk,
            filename,
        )

    def save(self, *args, **kwargs):
        super().save(*args, **kwargs)  # 기존의 save 호출

        s3 = boto3.client("s3")

        if self.logo:  # 로고 이미지가 있다면
            logo_image = Image.open(urllib.request.urlopen(self.logo.url))
            logo_image.thumbnail((150, 150))  # 비율을 유지하면서 이미지 크기 조절

            logo_buffer = io.BytesIO()
            logo_image.save(logo_buffer, format=logo_image.format)  # 이미지 데이터를 메모리에 저장
            logo_buffer.seek(0)

            # S3에 이미지를 다시 업로드
            s3.upload_fileobj(
                logo_buffer,
                settings.AWS_STORAGE_BUCKET_NAME,
                self.logo.name,
                ExtraArgs={"ContentType": "image/{}".format(logo_image.format.lower())},
            )

        if self.banner:  # 배너 이미지가 있다면
            banner_image = Image.open(urllib.request.urlopen(self.banner.url))
            banner_image.thumbnail((358, 176))  # 비율을 유지하면서 이미지 크기 조절

            banner_buffer = io.BytesIO()
            banner_image.save(
                banner_buffer, format=banner_image.format
            )  # 이미지 데이터를 메모리에 저장
            banner_buffer.seek(0)

            # S3에 이미지를 다시 업로드
            s3.upload_fileobj(
                banner_buffer,
                settings.AWS_STORAGE_BUCKET_NAME,
                self.banner.name,
                ExtraArgs={
                    "ContentType": "image/{}".format(banner_image.format.lower())
                },
            )

    company_user = models.ForeignKey("user.CompanyUser", on_delete=models.CASCADE)

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
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def clean(self):
        if self.duration < timedelta(days=7) or self.duration > timedelta(days=365):
            raise ValidationError("모집기간은 7과 365사이여야 합니다.")


class Activity(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE)

    title = models.CharField(max_length=20)
    kind = models.CharField(max_length=20)
    people_number = models.IntegerField()
    talent = models.TextField()
    frequency = models.TextField()
    way = models.TextField()
    period = models.DurationField()
    recruit = models.BooleanField(default=False)
    payment = models.CharField(
        max_length=50,
        null=True,
        blank=True,
    )


class Scrap(models.Model):
    student_user = models.ForeignKey("user.StudentUser", on_delete=models.CASCADE)
    board = models.ForeignKey(Board, on_delete=models.CASCADE)


class Form(models.Model):
    activity = models.ForeignKey(Activity, on_delete=models.CASCADE)
    student_user = models.ForeignKey("user.StudentUser", on_delete=models.CASCADE)

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

    introduce = models.TextField()
    reason = models.TextField()
    merit = models.TextField()
    is_accepted = models.CharField(
        max_length=10,
        choices=IS_ACCEPTED_CHOICES,
        default=PENDING,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
