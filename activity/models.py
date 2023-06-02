from django.db import models


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
    introduction = models.TextField()
    vision = models.TextField()
    pride = models.CharField(max_length=200)
    address = models.CharField(max_length=150)
    duration = models.DurationField()
    is_expired = models.BooleanField(default=False)


class Activity(models.Model):
    activity_id = models.AutoField(primary_key=True)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)

    title = models.CharField(max_length=20)
    kind = models.CharField(max_length=20)
    people_number = models.CharField(max_length=3)
    talent = models.TextField()
    frequency = models.TextField()
    way = models.TextField()
    period = models.CharField(max_length=3)
    recruit = models.BooleanField(default=True)
    payment = models.CharField(max_length=20)


class Scrap(models.Model):
    scrap_id = models.AutoField(primary_key=True)
    student_user_id = models.ForeignKey("user.StudentUser", on_delete=models.CASCADE)
    board_id = models.ForeignKey(Board, on_delete=models.CASCADE)


class Form(models.Model):
    form_id = models.AutoField(primary_key=True)
    activity_id = models.ForeignKey(Activity, on_delete=models.CASCADE)
    student_user_id = models.ForeignKey("user.StudentUser", on_delete=models.CASCADE)
    word = models.TimeField()
    is_accepted = models.BooleanField(default=False)
