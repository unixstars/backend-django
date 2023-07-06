from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError
from PIL import Image
import io
from django.core.files.base import ContentFile
from django.core.files.storage import default_storage as storage


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

    def save(self, *args, **kargs):
        super().save(*args, **kargs)
        # After save, read the file
        logo_read = storage.open(self.logo.name, "r")
        logo = Image.open(logo_read)
        if logo.height > 150 or logo.width > 150:
            size = 150, 150

            # Create a buffer to hold the bytes
            imageBuffer = io.BytesIO()

            # Resize
            logo.thumbnail(size, Image.ANTIALIAS)

            # Save the image as jpeg to the buffer
            logo.save(imageBuffer, logo.format)

            # Check whether it is resized
            logo.show()

            # Save the modified image
            board = Board.objects.get(pk=self.pk)
            board.logo.save(self.logo.name, ContentFile(imageBuffer.getvalue()))

            logo_read = storage.open(board.logo.name, "r")
            logo = Image.open(logo_read)
            logo.show()

        logo_read.close()

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
