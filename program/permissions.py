from rest_framework import permissions
from .models import AcceptedChatRoom, AcceptedMessage, AcceptedApplicant


class IsAcceptedMessageUser(permissions.BasePermission):
    def has_permission(self, request, view):
        chat_room_id = view.kwargs.get("chatroom_id")
        chatroom = AcceptedChatRoom.objects.get(id=chat_room_id)

        if not request.user.is_company_user:
            student_user_id = request.user.student_user.pk
            activity_id = chatroom.activity.pk
            return AcceptedApplicant.objects.filter(
                form__student_user__pk=student_user_id, activity__pk=activity_id
            ).exists()
        elif request.user.is_company_user:
            return chatroom.activity.board.company_user == request.user.company_user

        return False


class IsAcceptedChatRoomUser(permissions.BasePermission):
    def has_object_permission(self, request, view, obj):
        if not request.user.is_company_user:
            student_user_id = request.user.student_user.pk
            activity_id = obj.activity.pk
            return AcceptedApplicant.objects.filter(
                form__student_user__pk=student_user_id, activity__pk=activity_id
            ).exists()
        elif request.user.is_company_user:
            return obj.activity.board.company_user == request.user.company_user

        return False
