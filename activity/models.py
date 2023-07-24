from django.db import models
from datetime import timedelta
from django.core.exceptions import ValidationError
from PIL import Image
import io, os, sys
from django.core.files.uploadedfile import InMemoryUploadedFile
from user.models import CompanyUser, StudentUser
from django.utils import timezone


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
        # Check if logo or banner exists in the current instance in database
        try:
            this = Board.objects.get(id=self.id)
            if this.logo != self.logo:
                this.logo.delete(save=False)
            if this.banner != self.banner:
                this.banner.delete(save=False)
        except:
            pass

        for attr in ["logo", "banner"]:
            image_field = getattr(self, attr)
            # Check if image exists
            if image_field:
                # Read the file
                try:
                    image_read = image_field.file
                except ValueError:
                    # No file, don't process image, just save
                    super().save(*args, **kwargs)
                    return
                else:
                    image = Image.open(image_read)
                    image_format = (
                        os.path.splitext(image_field.name)[1].lstrip(".").upper()
                    )
                    if image_format == "JPG":
                        image_format = "JPEG"

                # Set the size. For logo, it's 150x150. For banner, it's 358x176.
                size = (150, 150) if attr == "logo" else (358, 176)

                # Create a buffer to hold the bytes
                imageBuffer = io.BytesIO()

                # Resize the image
                image = image.resize(size, Image.Resampling.LANCZOS)

                # Save the image as jpeg to the buffer
                image.save(imageBuffer, image_format)
                imageBuffer.seek(0)

                # Replace the ImageField file with the new resized file
                setattr(
                    self,
                    attr,
                    InMemoryUploadedFile(
                        imageBuffer,
                        "ImageField",
                        "%s.%s"
                        % (image_field.name.split(".")[0], image_format.lower()),
                        "image/%s" % image_format.lower(),
                        sys.getsizeof(imageBuffer),
                        None,
                    ),
                )
        super().save(*args, **kwargs)

    company_user = models.ForeignKey(
        CompanyUser, on_delete=models.CASCADE, related_name="board"
    )

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
        max_length=300,
        null=True,
        blank=True,
    )
    address = models.CharField(max_length=150)
    duration = models.DurationField()
    is_expired = models.BooleanField(default=False)
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration_extended = models.IntegerField(default=0)

    def update_expired_status(self):
        deadline = self.created_at + self.duration
        if timezone.now() > deadline and not self.is_expired:
            self.is_expired = True
            self.save()

    def __str__(self):
        return self.company_name

    def clean(self):
        if self.duration < timedelta(days=7) or self.duration > timedelta(days=365):
            raise ValidationError("모집기간은 7과 365사이여야 합니다.")


class Activity(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="activity")

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
        default="없음",
    )


class Scrap(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="scrap")
    student_user = models.ForeignKey(
        StudentUser, on_delete=models.CASCADE, related_name="scrap"
    )


class Form(models.Model):
    student_user = models.ForeignKey(
        StudentUser, on_delete=models.SET_NULL, null=True, related_name="form"
    )
    activity = models.ForeignKey(
        Activity, on_delete=models.SET_NULL, null=True, related_name="form"
    )

    PENDING, WAITING, CANCELED, REJECTED, ACCEPTED = (
        "pending",
        "waiting",
        "canceled",
        "rejected",
        "accepted",
    )

    ACCEPT_STATUS_CHOICES = [
        (PENDING, "대기중"),
        (WAITING, "확정대기"),
        (CANCELED, "활동취소"),
        (REJECTED, "불합격"),
        (ACCEPTED, "합격"),
    ]

    introduce = models.TextField()
    reason = models.TextField()
    merit = models.TextField()
    accept_status = models.CharField(
        max_length=10,
        choices=ACCEPT_STATUS_CHOICES,
        default=PENDING,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)
