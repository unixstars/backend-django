from django.db import models
from activity.models import Form


class Assignment(models.Model):
    form = models.OneToOneField(Form, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)


class Notice(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NoticeComment(models.Model):
    notice = models.ForeignKey(Notice, on_delete=models.CASCADE)

    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WeekAssign(models.Model):
    assignment = models.ForeignKey(Assignment, on_delete=models.CASCADE)

    title = models.CharField(max_length=30)
    content = models.TextField()
    week = models.IntegerField()
    is_approve = models.BooleanField(default=False)


class SubmitFiles(models.Model):
    week_assign = models.OneToOneField(WeekAssign, on_delete=models.CASCADE)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SubmitOneFile(models.Model):
    def get_upload_path_files(instance, filename):
        return "student/{}/activity/{}/assginment/{}/week/{}/submit_files/{}".format(
            instance.submitfiles.week_assign.assignment.form.student_user.pk,
            instance.submitfiles.week_assign.assignment.form.activity.pk,
            instance.submitfiles.week_assign.assignment.pk,
            instance.submitfiles.week_assign.pk,
            filename,
        )

    submitfiles = models.ForeignKey(SubmitFiles, on_delete=models.CASCADE)

    file = models.FileField()
