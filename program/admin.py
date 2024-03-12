from django.contrib import admin
from .models import (
    AcceptedApplicant,
    ApplicantWarning,
    Notice,
    NoticeComment,
    Assignment,
    AssignmentComment,
    Submit,
    SubmitFile,
)


@admin.register(AcceptedApplicant)
class AcceptedApplicantAdmin(admin.ModelAdmin):
    list_display = ["form", "week", "activity_status"]


@admin.register(ApplicantWarning)
class ApplicantWarningAdmin(admin.ModelAdmin):
    list_display = ["accepted_applicant"]


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ["accepted_applicant", "title"]


@admin.register(NoticeComment)
class NoticeCommentAdmin(admin.ModelAdmin):
    list_display = ["notice"]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["activity", "title", "created_at", "updated_at"]


@admin.register(AssignmentComment)
class AssignmentCommentAdmin(admin.ModelAdmin):
    list_display = ["assignment"]


@admin.register(Submit)
class SubmitAdmin(admin.ModelAdmin):
    list_display = ["accepted_applicant", "assignment", "created_at", "updated_at"]


@admin.register(SubmitFile)
class SubmitFileAdmin(admin.ModelAdmin):
    list_display = ["submit", "created_at"]
