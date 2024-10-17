from django.contrib import admin
from .models import (
    AcceptedApplicant,
    ApplicantWarning,
    Notice,
    Assignment,
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
    list_display = ["activity", "title"]


@admin.register(Assignment)
class AssignmentAdmin(admin.ModelAdmin):
    list_display = ["activity", "title", "created_at", "updated_at"]


@admin.register(Submit)
class SubmitAdmin(admin.ModelAdmin):
    list_display = ["assignment", "accepted_applicant", "progress_status"]


@admin.register(SubmitFile)
class SubmitFileAdmin(admin.ModelAdmin):
    list_display = ["submit", "created_at"]
