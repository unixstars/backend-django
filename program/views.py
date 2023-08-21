from rest_framework import generics, status, parsers
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
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
    ProgramWarningSerializer,
    NoticeDetailSerializer,
    NoticeCommentSerializer,
    NoticeCommentCreateSerializer,
    AssignmentDetailSerializer,
    AssignmentCommentSerializer,
    AssignmentCommentCreateSerializer,
    SubmitCreateSerializer,
    SubmitUpdateSerializer,
    CompanyProgramListSerializer,
    CompanyProgramDetailSerializer,
    CompanyProgramApplicantDetailSerializer,
    CompanyProgramApplicantWarningSerializer,
    CompanyProgramWarningCreateSerializer,
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
        return AcceptedApplicant.objects.filter(form__student_user=user).exclude(
            activity_status="canceled"
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


# 나의활동/활동1/공지: 공지
class NoticeDetailView(generics.RetrieveAPIView):
    serializer_class = NoticeDetailSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        user = self.request.user.student_user
        program_id = self.kwargs.get("program_id")
        return Notice.objects.filter(
            accepted_applicant__pk=program_id,
            accepted_applicant__form__student_user=user,
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
        user = self.request.user.student_user
        program_id = self.kwargs.get("program_id")
        return Assignment.objects.filter(
            accepted_applicant__pk=program_id,
            accepted_applicant__form__student_user=user,
        )


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
        IsSubmitOwnerStudent,
    ]
    parser_classes = [parsers.MultiPartParser, parsers.FormParser]

    def create(self, request, *args, **kwargs):
        assignment_id = self.kwargs.get("assignment_id")
        assignment = Assignment.objects.get(pk=assignment_id)

        if assignment.progress_status != Assignment.IN_PROGRESS:
            return Response(
                {"detail": "과제 제출은 처음만 가능합니다. 이후엔 수정 제출 해야 합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        assignment_id = self.kwargs.get("assignment_id")
        assignment = Assignment.objects.get(pk=assignment_id)
        serializer.save(assignment=assignment)


# 나의활동/활동1/과제/수정: 과제 수정
class SubmitUpdateView(generics.UpdateAPIView):
    serializer_class = SubmitUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsSubmitOwnerStudent,
    ]

    def get_queryset(self):
        assignment_id = self.kwargs.get("assignment_id")
        # __in을 사용하여 특정 progress_status를 가진 인스턴스만 필터링
        return Submit.objects.filter(
            assignment__pk=assignment_id,
            assignment__progress_status__in=[
                Assignment.FIRST_REVISION,
                Assignment.SECOND_REVISION,
            ],
        )


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


# 활동관리/활동1: 활동1 참여자 리스트
class CompanyProgramDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        user = self.request.user.company_user
        has_accepted_applicant = AcceptedApplicant.objects.filter(
            form__activity=OuterRef("pk")
        ).values("pk")

        return Activity.objects.filter(
            Exists(has_accepted_applicant), board__company_user=user
        )


# 활동관리/활동1/학생1: 공지,과제 리스트
class CompanyProgramApplicantDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramApplicantDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        activity_id = self.kwargs.get("activity_id")
        return AcceptedApplicant.objects.filter(form__activity__pk=activity_id).exclude(
            activity_status="canceled"
        )


# 활동관리/활동1/학생1/경고: 부여한 경고 리스트
class CompanyProgramApplicantWarningView(generics.RetrieveAPIView):
    serializer_class = CompanyProgramApplicantWarningSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        activity_id = self.kwargs.get("activity_id")
        return AcceptedApplicant.objects.filter(form__activity__pk=activity_id).exclude(
            activity_status="canceled"
        )


# 활동관리/활동1/학생1/경고/경고하기: 경고 부여하기
class CompanyProgramWarningCreateView(generics.CreateAPIView):
    serializer_class = CompanyProgramWarningCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def perform_create(self, serializer):
        applicant_id = self.kwargs.get("applicant_id")
        applicant = AcceptedApplicant.objects.get(pk=applicant_id)
        serializer.save(accepted_applicant=applicant)


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

        if original_deadline > timezone.now():
            assignment.duration += timedelta(days=3)
        else:
            assignment.duration = (
                timezone.now() - assignment.created_at + timedelta(days=3)
            )

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
        if assignment.progress_status == Assignment.FIRST_REVISION:
            assignment.progress_status = Assignment.SECOND_REVISION
            assignment.save()
        else:
            return Response(
                {"detail": "수정 요청은 과제 상태가 진행중 또는 1차 수정일때만 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        return Response(status=status.HTTP_200_OK)


# 활동관리/활동1/학생1/과제/최종 승인: 과제 최종승인
class CompanyProgramAssignmentApprovalView(generics.UpdateAPIView):
    queryset = Assignment.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        assignment = self.get_object()

        if assignment.prgress_status == Assignment.FINAL_APPROVAL:
            return Response(
                {"detail": "이미 최종 승인된 상태입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        assignment.prgress_status = Assignment.FINAL_APPROVAL
        assignment.save()

        return Response(status=status.HTTP_200_OK)
