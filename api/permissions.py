# permissions.py
from rest_framework import permissions


class IsCompanyUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and request.user.is_company_user
        )


class IsStudentUser(permissions.BasePermission):
    def has_permission(self, request, view):
        return bool(
            request.user
            and request.user.is_authenticated
            and not request.user.is_company_user
        )


class IsBoardOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.company_user.user == request.user


class IsFormOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student_user.user == request.user


class IsProfileOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student_user.user == request.user


class IsPortFolioOwner(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.student_user.user == request.user


class IsSubmitOwnerStudent(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        return obj.assignment.accepted_applicant.form.student_user.user == request.user


class IsStaffOrReadOnly(permissions.BasePermission):
    def has_permission(self, request, view):
        if request.method == "GET":
            return True
        return request.user.is_authenticated and request.user.is_staff


class IsStaff(permissions.BasePermission):
    def has_permission(self, request, view):
        return request.user.is_authenticated and request.user.is_staff
