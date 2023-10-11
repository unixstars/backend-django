from django.contrib import admin
from .models import (
    User,
    StudentUser,
    StudentUserProfile,
    StudentUserPortfolio,
    CompanyUser,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "username", "is_staff"]
    search_fields = ["email", "username"]


@admin.register(StudentUser)
class StudentUserAdmin(admin.ModelAdmin):
    list_display = ["user"]
    search_fields = ["user"]


@admin.register(StudentUserProfile)
class StudentUserProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "university", "major"]
    search_fields = ["name", "university", "major"]


@admin.register(StudentUserPortfolio)
class StudentUserPortfolioAdmin(admin.ModelAdmin):
    list_display = ["title", "content"]
    search_fields = ["title"]


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ["user", "business_number", "ceo_name"]
    search_fields = ["user", "business_number", "ceo_name"]
