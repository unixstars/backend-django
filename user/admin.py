from django.contrib import admin
from .models import (
    User,
    StudentUser,
    StudentUserProfile,
    StudentUserPortfolio,
    CompanyUser,
    PortfolioFile,
)


@admin.register(User)
class UserAdmin(admin.ModelAdmin):
    list_display = ["email", "is_staff", "created_at"]
    search_fields = ["email"]


@admin.register(StudentUser)
class StudentUserAdmin(admin.ModelAdmin):
    list_display = ["user"]
    search_fields = ["user"]


@admin.register(StudentUserProfile)
class StudentUserProfileAdmin(admin.ModelAdmin):
    list_display = ["name", "student_user", "university", "major"]
    search_fields = ["name", "university", "major"]


@admin.register(StudentUserPortfolio)
class StudentUserPortfolioAdmin(admin.ModelAdmin):
    list_display = ["title", "content"]
    search_fields = ["title"]


@admin.register(PortfolioFile)
class StudentUserPortfolioFileAdmin(admin.ModelAdmin):
    list_display = ["student_user_portfolio"]


@admin.register(CompanyUser)
class CompanyUserAdmin(admin.ModelAdmin):
    list_display = ["user", "business_number", "ceo_name"]
    search_fields = ["user", "business_number", "ceo_name"]
