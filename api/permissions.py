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
