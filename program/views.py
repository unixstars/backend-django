from rest_framework import generics, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.db.models import Exists, OuterRef
from django.utils import timezone
from datetime import timedelta
from api.permissions import (
    IsStudentUser,
    IsCompanyUser,
    IsNoticeCommentStudent,
    IsAssignmentCommentStudent,
    IsNoticeCommentCompany,
    IsAssignmentCommentCompany,
    IsSubmitOwnerStudent,
)
from .models import (
    AcceptedApplicant,
    ApplicantWarning,
    ApplicantComment,
    Notice,
    NoticeComment,
    Assignment,
    AssignmentComment,
    Submit,
)
from activity.models import Activity
from .serializers import (
    ProgramListSerializer,
    ProgramDetailSerializer,
    ApplicantCommentListSerializer,
    ApplicantCommentCreateSerializer,
    ProgramWarningSerializer,
    NoticeDetailSerializer,
    NoticeCommentSerializer,
    NoticeCommentCreateSerializer,
    AssignmentDetailSerializer,
    AssignmentCommentSerializer,
    AssignmentCommentCreateSerializer,
    SubmitCreateSerializer,
    SubmitUpdateSerializer,
    OtherSubmitListSerializer,
    OtherSubmitDetailSerializer,
    CompanyProgramListSerializer,
    CompanyProgramDetailSerializer,
    CompanyProgramWarningSerializer,
    CompanyProgramWarningCreateSerializer,
    CompanyApplicantCommentListSerializer,
    CompanyApplicantCommentCreateSerializer,
    CompanyProgramNoticeDetailSerializer,
    CompanyProgramNoticeCreateSerializer,
    CompanyProgramNoticeCommentCreateSerializer,
    CompanyProgramAssignmentDetailSerializer,
    CompanyProgramAssignmentCreateSerializer,
    CompanyProgramAssignmentCommentCreateSerializer,
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


# 나의활동/활동1/경고: 받은 경고 리스트
class ProgramWarningView(generics.ListAPIView):
    serializer_class = ProgramWarningSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        user = self.request.user.student_user
        program_id = self.kwargs.get("program_id")
        return ApplicantWarning.objects.filter(
            accepted_applicant__pk=program_id,
            accepted_applicant__form__student_user=user,
        )


# 나의활동/활동1/소통댓글창
class ApplicantCommentListView(generics.ListAPIView):
    serializer_class = ApplicantCommentListSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        program_id = self.kwargs.get("program_id")
        activity = Activity.objects.get(form__accepted_applicant__pk=program_id)
        return (
            ApplicantComment.objects.filter(activity=activity)
            .select_related(
                "accepted_applicant__form__student_user__student_user_profile",
                "activity__board__company_user",
            )
            .order_by("created_at")
        )


# 나의활동/활동1/소통댓글창/등록 : 학생 댓글 등록
class ApplicantCommentCreateView(generics.CreateAPIView):
    serializer_class = ApplicantCommentCreateSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def perform_create(self, serializer):
        user = self.request.user.student_user
        program_id = self.kwargs.get("program_id")
        activity = Activity.objects.get(form__accepted_applicant__pk=program_id)
        applicant = AcceptedApplicant.objects.get(form__student_user=user)
        return serializer.save(
            activity=activity,
            accepted_applicant=applicant,
            user_type=ApplicantComment.STUDENT,
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


# (학생,기업) 공지 댓글 리스트
class NoticeCommentListView(generics.ListAPIView):
    serializer_class = NoticeCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        notice_id = self.kwargs.get("notice_id")
        return NoticeComment.objects.filter(notice__pk=notice_id).order_by("created_at")


# 나의활동/활동1/공지/댓글 작성: 공지 댓글 작성
class NoticeCommentCreateView(generics.CreateAPIView):
    serializer_class = NoticeCommentCreateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsNoticeCommentStudent,
    ]

    def perform_create(self, serializer):
        notice_id = self.kwargs.get("notice_id")
        notice = Notice.objects.get(pk=notice_id)
        serializer.save(notice=notice)


# 나의활동/활동1/공지/공지 확인: 공지 확인 버튼
class NoticeCheckUpdateView(generics.UpdateAPIView):
    queryset = Notice.objects.all()
    permission_classes = [IsAuthenticated, IsStudentUser]

    def update(self, request, *args, **kwargs):
        notice = self.get_object()
        if notice.accepted_applicant.form.student_user.user != request.user:
            return Response(
                {"detail": "해당 활동에 참여한 학생이 아닙니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        notice.is_checked = True
        notice.save()
        return Response(status=status.HTTP_200_OK)


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


# (학생,기업) 과제 댓글 리스트
class AssignmentCommentListView(generics.ListAPIView):
    serializer_class = AssignmentCommentSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        assignment_id = self.kwargs.get("assignment_id")
        return AssignmentComment.objects.filter(assignment__pk=assignment_id).order_by(
            "created_at"
        )


# 나의활동/활동1/과제/댓글 작성: 과제 댓글 작성
class AssignmentCommentCreateView(generics.CreateAPIView):
    serializer_class = AssignmentCommentCreateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsAssignmentCommentStudent,
    ]

    def perform_create(self, serializer):
        assignment_id = self.kwargs.get("assignment_id")
        assignment = Assignment.objects.get(pk=assignment_id)
        serializer.save(assignment=assignment)


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


# 활동관리/활동1/소통 댓글창: 해당 대외활동 참여자 및 기업 댓글 리스트
class CompanyApplicantCommentListView(generics.ListAPIView):
    serializer_class = CompanyApplicantCommentListSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        activity_id = self.kwargs.get("activity_id")
        return (
            ApplicantComment.objects.filter(activity__pk=activity_id)
            .select_related(
                "accepted_applicant__form__student_user__student_user_profile",
                "activity__board__company_user",
            )
            .order_by("created_at")
        )


# 활동관리/활동1/소통 댓글창/등록: 기업 댓글 등록
class CompanyApplicantCommentCreateView(generics.CreateAPIView):
    serializer_class = CompanyApplicantCommentCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def perform_create(self, serializer):
        company_user = self.request.user.company_user
        activity_id = self.kwargs.get("activity_id")
        try:
            activity = Activity.objects.get(
                pk=activity_id, board__company_user=company_user
            )
        except Activity.DoesNotExist:
            raise NotFound(
                detail="해당 대외활동을 가진 기업만 댓글을 작성할 수 있습니다.",
                code=404,
            )

        return serializer.save(
            activity=activity,
            user_type=ApplicantComment.COMPANY,
        )


# 활동관리/활동1/학생1/공지: 공지
class CompanyProgramNoticeDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramNoticeDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        applicant_id = self.kwargs.get("applicant_id")
        return Notice.objects.filter(accepted_applicant__pk=applicant_id)


# 활동관리/활동1/학생1/공지/공지 작성: 공지 작성
class CompanyProgramNoticeCreateView(generics.CreateAPIView):
    serializer_class = CompanyProgramNoticeCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def perform_create(self, serializer):
        applicant_id = self.kwargs.get("applicant_id")
        applicant = AcceptedApplicant.objects.get(pk=applicant_id)
        serializer.save(accepted_applicant=applicant)


# 활동관리/활동1/학생1/공지/댓글 작성: 공지 댓글 작성
class CompanyProgramNoticeCommentCreateView(generics.CreateAPIView):
    serializer_class = CompanyProgramNoticeCommentCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser, IsNoticeCommentCompany]

    def perform_create(self, serializer):
        notice_id = self.kwargs.get("notice_id")
        notice = Notice.objects.get(pk=notice_id)
        serializer.save(notice=notice, user_type=NoticeComment.COMPANY)


# 활동관리/활동1/학생1/과제: 과제
class CompanyProgramAssignmentDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramAssignmentDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        applicant_id = self.kwargs.get("applicant_id")
        applicant = AcceptedApplicant.objects.get(pk=applicant_id)
        return Assignment.objects.filter(accepted_applicant=applicant)


# 활동관리/활동1/학생1/과제/과제 작성: 과제 작성
class CompanyProgramAssignmentCreateView(generics.CreateAPIView):
    serializer_class = CompanyProgramAssignmentCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def perform_create(self, serializer):
        applicant_id = self.kwargs.get("applicant_id")
        applicant = AcceptedApplicant.objects.get(pk=applicant_id)
        serializer.save(accepted_applicant=applicant)


# 활동관리/활동1/학생1/과제/댓글 작성: 과제 댓글 작성
class CompanyProgramAssignmentCommentCreateView(generics.CreateAPIView):
    serializer_class = CompanyProgramAssignmentCommentCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser, IsAssignmentCommentCompany]

    def perform_create(self, serializer):
        assignment_id = self.kwargs.get("assignment_id")
        assignment = Assignment.objects.get(pk=assignment_id)
        serializer.save(assignment=assignment, user_type=AssignmentComment.COMPANY)


# 활동관리/활동1/학생1/과제: 과제 마감기한 연장
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


# 활동관리/활동1/학생1/과제/수정요구: 과제 수정요구(1,2차)
class CompanyProgramAssignmentRevisionView(generics.UpdateAPIView):
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        assignment = self.get_object()

        if assignment.progress_status == Assignment.IN_PROGRESS:
            assignment.progress_status = Assignment.FIRST_REVISION
            assignment.save()
        elif assignment.progress_status == Assignment.FIRST_REVISION:
            assignment.progress_status = Assignment.SECOND_REVISION
            assignment.save()
        else:
            return Response(
                {
                    "detail": "수정 요청은 과제 상태가 진행중 또는 1차 수정일때만 가능합니다."
                },
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)


# 활동관리/활동1/학생1/과제/최종 승인: 과제 최종승인
class CompanyProgramAssignmentApprovalView(generics.UpdateAPIView):
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        assignment = self.get_object()

        if assignment.progress_status == Assignment.FINAL_APPROVAL:
            return Response(
                {"detail": "이미 최종 승인된 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment.progress_status = Assignment.FINAL_APPROVAL
        assignment.save()

        return Response(status=status.HTTP_200_OK)
