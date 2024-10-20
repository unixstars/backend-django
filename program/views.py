from rest_framework import generics, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.db.models import Exists, OuterRef
from django.utils import timezone
from datetime import timedelta
from .permissions import IsAcceptedMessageUser, IsAcceptedChatRoomUser
from api.permissions import (
    IsStudentUser,
    IsCompanyUser,
)
from .models import (
    AcceptedApplicant,
    ApplicantWarning,
    Notice,
    Assignment,
    Submit,
    AcceptedChatRoom,
    AcceptedMessage,
)
from .paginations import MessageListPagination
from activity.models import Activity
from .serializers import (
    ProgramListSerializer,
    ProgramDetailSerializer,
    NoticeDetailSerializer,
    AssignmentDetailSerializer,
    SubmitCreateSerializer,
    SubmitUpdateSerializer,
    OtherSubmitListSerializer,
    OtherSubmitDetailSerializer,
    CompanyProgramListSerializer,
    CompanyProgramDetailSerializer,
    CompanyProgramWarningSerializer,
    CompanyProgramWarningCreateSerializer,
    CompanyProgramNoticeDetailSerializer,
    CompanyProgramNoticeCreateSerializer,
    CompanyProgramAssignmentSubmitListSerializer,
    CompanyProgramAssignmentSubmitDetailSerializer,
    CompanyProgramAssignmentDetailSerializer,
    CompanyProgramAssignmentCreateSerializer,
    AcceptedChatRoomSerializer,
    AcceptedMessageSerializer,
)


##학생
# 나의활동: 진행중,완료활동 리스트
class ProgramListView(generics.ListAPIView):
    serializer_class = ProgramListSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        user = self.request.user.student_user
        return AcceptedApplicant.objects.filter(form__student_user=user).exclude(
            activity_status="canceled"
        )


# 나의활동/활동1: 공지,과제 리스트
class ProgramDetailView(generics.RetrieveAPIView):
    serializer_class = ProgramDetailSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        user = self.request.user.student_user
        return (
            AcceptedApplicant.objects.filter(form__student_user=user)
            .exclude(activity_status="canceled")
            .select_related("form__activity__board")
            .prefetch_related(
                "form__activity__notice",
                "form__activity__assignment",
            )
        )


# 나의활동/활동1/공지: 공지
class NoticeDetailView(generics.RetrieveAPIView):
    serializer_class = NoticeDetailSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        program_id = self.kwargs.get("program_id")
        return Notice.objects.filter(
            activity__form__accepted_applicant__pk=program_id,
        )


# 나의활동/활동1/과제: 과제
class AssignmentDetailView(generics.RetrieveAPIView):
    serializer_class = AssignmentDetailSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        program_id = self.kwargs.get("program_id")
        return Assignment.objects.filter(
            activity__form__accepted_applicant__pk=program_id,
        )

    def get_serializer_context(self):
        context = super(AssignmentDetailView, self).get_serializer_context()
        context["program_id"] = self.kwargs.get("program_id")
        context["assignment_id"] = self.kwargs.get("pk")
        return context


# 나의활동/활동1/과제/과제제출: 과제 제출 버튼
class SubmitCreateView(generics.CreateAPIView):
    serializer_class = SubmitCreateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
    ]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def create(self, request, *args, **kwargs):
        program_id = self.kwargs.get("program_id")
        assignment_id = self.kwargs.get("assignment_id")

        if Submit.objects.filter(
            accepted_applicant__pk=program_id,
            assignment__pk=assignment_id,
            progress_status=Submit.IN_PROGRESS,
        ).exists():
            return Response(
                {
                    "detail": "과제 제출은 처음만 가능합니다. 이후엔 수정 제출 해야 합니다."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        program_id = self.kwargs.get("program_id")
        assignment_id = self.kwargs.get("assignment_id")
        program = AcceptedApplicant.objects.get(pk=program_id)
        assignment = Assignment.objects.get(pk=assignment_id)
        serializer.save(assignment=assignment, accepted_applicant=program)


# 나의활동/활동1/과제/수정: 과제 수정
class SubmitUpdateView(generics.UpdateAPIView):
    serializer_class = SubmitUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
    ]

    def get_object(self):
        program_id = self.kwargs.get("program_id")
        assignment_id = self.kwargs.get("assignment_id")
        # __in을 사용하여 특정 progress_status를 가진 인스턴스만 필터링
        try:
            submit = Submit.objects.filter(
                progress_status__in=[
                    Submit.FIRST_REVISION,
                    Submit.SECOND_REVISION,
                ]
            ).get(accepted_applicant__pk=program_id, assignment__pk=assignment_id)
            return submit
        except Submit.DoesNotExist:
            raise NotFound(detail="수정할 수 있는 과제 제출물이 존재하지 않습니다.")


# 과제/다른사람 제출물 : 해당 과제 다른 참여자 과제 제목 리스트
class OtherSubmitListView(generics.ListAPIView):
    serializer_class = OtherSubmitListSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
    ]

    def get_queryset(self):
        program_id = self.kwargs.get("program_id")
        assignment_id = self.kwargs.get("assignment_id")
        return (
            Submit.objects.filter(assignment__pk=assignment_id)
            .exclude(accepted_applicant__pk=program_id)
            .select_related(
                "accepted_applicant__form__student_user__student_user_profile",
                "assignment",
            )
        )


# 과제/다른사람제출물/사람1 : 사람1 과제 내용
class OtherSubmitDetailView(generics.RetrieveAPIView):
    serializer_class = OtherSubmitDetailSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
    ]

    def get_object(self):
        program_id = self.kwargs.get("program_id")
        assignment_id = self.kwargs.get("assignment_id")
        submit_id = self.kwargs.get("submit_id")
        return (
            Submit.objects.filter(assignment__pk=assignment_id)
            .exclude(accepted_applicant__pk=program_id)
            .select_related(
                "accepted_applicant__form__student_user__student_user_profile",
                "assignment",
            )
            .get(pk=submit_id)
        )


############################################################################################################################


##기업
# 활동관리: 진행중, 완료활동 리스트
class CompanyProgramListView(generics.ListAPIView):
    serializer_class = CompanyProgramListSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        user = self.request.user.company_user

        # AcceptedApplicant가 존재하는 Form을 찾는 서브쿼리
        # 서브쿼리: 한 쿼리 내에서 다른 쿼리의 결과를 사용하기 위한 쿼리
        # OuterRef를 통해 바깥 쿼리인 Activity의 pk 참조, .values로 해당하는 pk목록 가져옴
        # Exist()(SQL EXIST 생성)를 통해 해당 조건에 맞는 쿼리 생성
        has_accepted_applicant = AcceptedApplicant.objects.filter(
            form__activity=OuterRef("pk")
        ).values("pk")

        return Activity.objects.filter(
            Exists(has_accepted_applicant), board__company_user=user
        )


# 활동관리/활동1/활동 시작: 대외활동 시작
class CompanyProgramStartView(generics.UpdateAPIView):
    queryset = Activity.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        activity = self.get_object()
        applicants = AcceptedApplicant.objects.filter(form__activity=activity)

        for applicant in applicants:
            applicant.week = 1
            applicant.start_date = timezone.now().date()
            applicant.save()

        return Response(status=status.HTTP_200_OK)


# 활동관리/활동1: 공지,과제 리스트
class CompanyProgramDetaillView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_object(self):
        activity_id = self.kwargs.get("activity_id")
        return (
            Activity.objects.select_related("board")
            .prefetch_related("form__accepted_applicant", "assignment", "notice")
            .get(pk=activity_id)
        )


# 활동관리/활동1/참여자 경고 부여 : 참여자 경고 부여 화면창
class CompanyProgramWarningView(generics.ListAPIView):
    serializer_class = CompanyProgramWarningSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        activity_id = self.kwargs.get("activity_id")
        return (
            AcceptedApplicant.objects.filter(form__activity__pk=activity_id)
            .exclude(activity_status=AcceptedApplicant.CANCELED)
            .select_related("form__student_user__student_user_profile")
            .prefetch_related("applicant_warning")
        )


# 활동관리/활동1/경고 부여하기: 참여자 한명 경고 부여하기
class CompanyProgramWarningCreateView(generics.CreateAPIView):
    serializer_class = CompanyProgramWarningCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        activity_id = self.kwargs.get("activity_id")
        return ApplicantWarning.objects.filter(
            accepted_applicant__form__activity__pk=activity_id
        )


# 활동관리/활동1/공지: 공지
class CompanyProgramNoticeDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramNoticeDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        activity_id = self.kwargs.get("activity_id")
        return Notice.objects.filter(activity__pk=activity_id)


# 활동관리/활동1/학생1/공지/공지 작성: 공지 작성
class CompanyProgramNoticeCreateView(generics.CreateAPIView):
    serializer_class = CompanyProgramNoticeCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def perform_create(self, serializer):
        activity_id = self.kwargs.get("activity_id")
        activity = Activity.objects.get(pk=activity_id)
        serializer.save(activity=activity)


# 활동관리/활동1/과제: 과제
class CompanyProgramAssignmentDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramAssignmentDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        activity_id = self.kwargs.get("activity_id")
        return Assignment.objects.filter(activity__pk=activity_id)


# 활동관리/활동1/과제/과제 작성: 과제 작성
class CompanyProgramAssignmentCreateView(generics.CreateAPIView):
    serializer_class = CompanyProgramAssignmentCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def perform_create(self, serializer):
        activity_id = self.kwargs.get("activity_id")
        activity = Activity.objects.get(pk=activity_id)
        serializer.save(activity=activity)


# N: 등록된 과제/과제 제출자
class CompanyProgramAssignmentSubmitListView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramAssignmentSubmitListSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_object(self):
        assignment_id = self.kwargs.get("assignment_id")
        return (
            Assignment.objects.select_related("activity__board")
            .prefetch_related("activity__form__accepted_applicant")
            .get(pk=assignment_id)
        )


# N: 등록된 과제/과제 제출자/제출 내용
class CompanyProgramAssignmentSubmitDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramAssignmentSubmitDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        assignment_id = self.kwargs.get("assignment_id")
        return Submit.objects.filter(assignment__pk=assignment_id).select_related(
            "accepted_applicant__form__student_user__student_user_profile", "assignment"
        )


# 활동관리/활동1/과제/마감기한 연장
class CompanyProgramAssignmentDurationExtendView(generics.UpdateAPIView):
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        assignment = self.get_object()
        original_deadline = assignment.created_at + assignment.duration

        if assignment.duration_extended >= 3:
            return Response(
                {"detail": "기한연장은 최대 3번까지만 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if original_deadline > timezone.now():
            assignment.duration += timedelta(days=3)
            assignment.duration_extended += 1
        else:
            assignment.duration = (
                timezone.now() - assignment.created_at + timedelta(days=3)
            )
            assignment.duration_extended += 1

        assignment.save()
        return Response(status=status.HTTP_200_OK)


# 등록된 과제/과제 제출자/수정요구: 제출 수정요구(1,2차)
class CompanyProgramSubmitRevisionView(generics.UpdateAPIView):
    queryset = Submit.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        submit = self.get_object()

        if submit.progress_status == Submit.IN_PROGRESS:
            submit.progress_status = Submit.FIRST_REVISION
            submit.save()
        elif submit.progress_status == Submit.FIRST_REVISION:
            submit.progress_status = Submit.SECOND_REVISION
            submit.save()
        else:
            return Response(
                {
                    "detail": "수정 요청은 제출 상태가 진행중 또는 1차 수정일때만 가능합니다."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)


# 등록된 과제/과제 제출자/최종 승인: 제출 최종승인
class CompanyProgramSubmitApprovalView(generics.UpdateAPIView):
    queryset = Submit.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        submit = self.get_object()

        if submit.progress_status == Submit.FINAL_APPROVAL:
            return Response(
                {"detail": "이미 최종 승인된 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        submit.progress_status = Submit.FINAL_APPROVAL
        submit.save()

        return Response(status=status.HTTP_200_OK)


class AcceptedMessageListCreateView(generics.ListCreateAPIView):
    serializer_class = AcceptedMessageSerializer
    permission_classes = [IsAuthenticated, IsAcceptedMessageUser]
    pagination_class = MessageListPagination

    def get_queryset(self):
        accepted_chatroom_id = self.kwargs.get("chatroom_id")
        return AcceptedMessage.objects.filter(
            accepted_chatroom__pk=accepted_chatroom_id
        ).order_by("created_at")

    def list(self, request, *args, **kwargs):
        response = super().list(request, *args, **kwargs)

        accepted_chatroom_id = self.kwargs.get("chatroom_id")
        user = request.user

        # 현재 채팅방에서 is_read=False이고, author가 현재 사용자가 아닌 메시지들 찾기
        unread_messages = AcceptedMessage.objects.filter(
            accepted_chatroom__pk=accepted_chatroom_id, is_read=False
        ).exclude(author_id=user.id)

        unread_messages.update(is_read=True)

        return response

    def perform_create(self, serializer):
        user = self.request.user
        accepted_chatroom_id = self.kwargs.get("chatroom_id")
        chatroom = AcceptedChatRoom.objects.get(pk=accepted_chatroom_id)

        if user.is_company_user:
            author_id = user.pk
            author_name = user.company_user.board.company_name
            author_logo = (
                user.company_user.board.logo
                if hasattr(user.company_user, "board.logo")
                else None
            )
            user_type = "company"
        else:
            author_id = user.pk
            author_name = user.student_user.profile.name
            author_logo = (
                user.student_user.profile.profile_image
                if hasattr(user.student_user, "profile.profile_image")
                else None
            )
            user_type = "student"

        serializer.save(
            accepted_chatroom=chatroom,
            author_id=author_id,
            author_name=author_name,
            author_logo=author_logo,
            user_type=user_type,
        )


class AcceptedChatRoomListView(generics.ListAPIView):
    serializer_class = AcceptedChatRoomSerializer
    permission_classes = [IsAuthenticated, IsAcceptedChatRoomUser]

    def get_queryset(self):
        user = self.request.user

        if user.is_company_user:
            return AcceptedChatRoom.objects.filter(
                activity__board__company_user=user.company_user
            )
        else:
            return AcceptedChatRoom.objects.filter(
                activity__form__student_user=user.student_user
            )
