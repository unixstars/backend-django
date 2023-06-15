from django.db import models
from activity.models import Form


class Assignment(models.Model):
    assignment_id = models.AutoField(primary_key=True)
    form_id = models.OneToOneField(Form, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)


class Notice(models.Model):
    notice_id = models.AutoField(primary_key=True)
    assignment_id = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class NoticeComment(models.Model):
    notice_comment_id = models.AutoField(primary_key=True)
    notice_id = models.ForeignKey(Notice, on_delete=models.CASCADE)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class WeekAssign(models.Model):
    week_assign_id = models.AutoField(primary_key=True)
    assignment_id = models.ForeignKey(Assignment, on_delete=models.CASCADE)
    title = models.CharField(max_length=30)
    content = models.TextField()
    week = models.IntegerField()
    is_approve = models.BooleanField(default=False)


class SubmitFiles(models.Model):
    submitfiles_id = models.AutoField(primary_key=True)
    week_assign_id = models.OneToOneField(WeekAssign, on_delete=models.CASCADE)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class SubmitOneFile(models.Model):
    def get_upload_path_files(instance, filename):
        return "student/{}/activity/{}/assginment/{}/week/{}/submit_files/{}".format(
            instance.submitfiles_id.week_assign_id.assignment_id.form_id.student_user_id.pk,
            instance.submitfiles_id.week_assign_id.assignment_id.form_id.activity_id.pk,
            instance.submitfiles_id.week_assign_id.assignment_id.pk,
            instance.submitfiles_id.week_assign_id.pk,
            filename,
        )

    file_id = models.AutoField(primary_key=True)
    submitfiles_id = models.ForeignKey(SubmitFiles, on_delete=models.CASCADE)
    file = models.FileField()
