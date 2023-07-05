from django.contrib import admin
from .models import Board, Activity, Scrap, Form


@admin.register(Board)
class BoardAdmin(admin.ModelAdmin):
    list_display = ["company_user", "title", "company_name", "views", "created_at"]
    search_fields = ["company_user", "company_name"]


@admin.register(Activity)
class ActivityAdmin(admin.ModelAdmin):
    list_display = ["board", "title", "kind"]
    search_fields = ["board", "title", "kind"]


@admin.register(Scrap)
class ScrapAdmin(admin.ModelAdmin):
    list_display = ["student_user", "board"]


@admin.register(Form)
class FormAdmin(admin.ModelAdmin):
    list_display = ["activity", "student_user", "is_accepted"]
    search_fields = ["activity", "student_user", "is_accepted"]
