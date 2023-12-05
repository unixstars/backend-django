from django import forms
from django.contrib import admin
from .models import Board, Activity, Scrap, Form, Suggestion


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["company_user", "title", "company_name", "views", "created_at"]
    search_fields = ["company_user", "company_name"]
    list_filter = ["is_admitted"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["board", "title", "kind"]
    search_fields = ["board", "title", "kind"]


@admin.register(Scrap)
class ScrapAdmin(admin.ModelAdmin):
    list_display = ["student_user", "board"]


class FormForm(forms.ModelForm):
    class Meta:
        model = Form
        fields = "__all__"
        widgets = {
            "student_user_portfolio": forms.Select(attrs={"required": False}),
        }


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    form = FormForm
    list_display = ["activity", "student_user", "accept_status"]
    search_fields = ["activity", "student_user", "accept_status"]


@admin.register(Suggestion)
class SuggestionAdmin(admin.ModelAdmin):
    list_display = ["company_user", "student_user", "created_at"]
