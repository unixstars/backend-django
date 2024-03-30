from django.contrib import admin
from .models import (
    AcceptedApplicant,
    ApplicantWarning,
    ApplicantComment,
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


@admin.register(ApplicantComment)
class ApplicantCommentAdmin(admin.ModelAdmin):
    list_display = ["activity", "accepted_applicant", "user_type", "created_at"]


@admin.register(ApplicantWarning)
class ApplicantWarningAdmin(admin.ModelAdmin):
    list_display = ["accepted_applicant"]


@admin.register(Notice)
class NoticeAdmin(admin.ModelAdmin):
    list_display = ["activity", "title"]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["activity", "title", "created_at", "updated_at"]
