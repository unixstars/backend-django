from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Board, Scrap, Form, Activity, Suggestion
from .paginations import BoardListPagination, ProfileListPagination
from user.models import (
    StudentUser,
    CompanyUser,
    StudentUserProfile,
    StudentUserPortfolio,
)
from .serializers import (
    BoardListSerializer,
    BoardCreateSerializer,
    BoardDetailSerializer,
    ScrapSerializer,
    FormSerializer,
    FormBoardListSerializer,
    FormBoardDetailSerializer,
    FormFillSerializer,
    FormCreateSerializer,
    FormDetailSerializer,
    CompanyActivityListSerializer,
    CompanyActivityFormListSerializer,
    CompanyStudentProfileListSerializer,
    CompanyStudentProfileDetailSerializer,
    CompanyStudentPortfolioDetailSerializer,
    SuggestionSerializer,
    SuggestionListSerializer,
)
from api.permissions import (
    IsCompanyUser,
    IsStudentUser,
    IsBoardOwner,
    IsFormOwner,
    IsProfileOwner,
)
from program.models import AcceptedApplicant
from django.db.models import F
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404


"""
queryset : 모든 요청에 대해 일정한 데이터 셋일경우(정적)
get_queryset(): 요청에 따라 데이터셋이 다를 경우(로그인한 사용자에 따라 다른 데이터)
get_queryset()는 객체가 반환될 수 있는 범위를 제한(여러 개의 쿼리셋 반환), 따라서 url에서 pk를 이용하여 하나에 접근 가능
get_object(): 특정 쿼리셋 하나 반환
"""


# 홈/로그인 전 : 게시글 목록(전부)
class BoardListView(generics.ListAPIView):
    queryset = Board.objects.order_by("-views", "-created_at").all()
    serializer_class = BoardListSerializer
    permission_classes = [AllowAny]
    pagination_class = BoardListPagination


# 대외활동 게시글/로그인 전 : 게시글 하나(전부)
class BoardDetailView(generics.RetrieveAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardDetailSerializer
    permission_classes = [AllowAny]

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        instance.views = F("views") + 1
        instance.save()
        instance.refresh_from_db()
        serializer = self.get_serializer(instance)
        return Response(serializer.data)


# 대외활동 게시글 추가하기 : 게시글 생성
class BoardCreateView(generics.CreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def perform_create(self, serializer):
        company_user = CompanyUser.objects.get(user=self.request.user)
        serializer.save(company_user=company_user)


# 대외활동 게시글/마감기한 연장(7일) : 게시글 마감기한연장
class BoardDurationExtendView(generics.UpdateAPIView):
    queryset = Board.objects.all()
    permission_classes = [
        IsAuthenticated,
        IsCompanyUser,
        IsBoardOwner,
    ]

    def update(self, request, *args, **kwargs):
        board = self.get_object()
        original_deadline = board.created_at + board.duration

        if board.duration_extended >= 4:
            return Response(
                {"detail": "기한연장은 최대 4번까지만 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        if original_deadline > timezone.now():
            board.duration += timedelta(days=7)
        else:
            board.duration = timezone.now() - board.created_at + timedelta(days=7)

        board.duration_extended += 1
        board.save()

        return Response(status=status.HTTP_200_OK)


# 활동등록 : 기업유저가 등록한 게시글 리스트
class CompanyUserBoardListView(generics.ListAPIView):
    serializer_class = BoardListSerializer
    permission_classes = [
        IsAuthenticated,
        IsCompanyUser,
        IsBoardOwner,
    ]
    pagination_class = BoardListPagination

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(company_user__user=user)


# 대외활동 게시글 : 기업유저가 등록한 게시글 하나
class CompanyUserBoardDetailView(generics.RetrieveAPIView):
    serializer_class = BoardDetailSerializer
    permission_classes = [
        IsAuthenticated,
        IsCompanyUser,
        IsBoardOwner,
    ]

    def get_queryset(self):
        user = self.request.user
        return Board.objects.filter(company_user__user=user)


# 지원관리 : 기업유저가 등록한 '대외활동' 목록
class CompanyActivityListView(generics.ListAPIView):
    serializer_class = CompanyActivityListSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        user = self.request.user.company_user
        return Activity.objects.filter(board__company_user=user)


# 지원관리/대외활동1 : 등록한 대외활동 목록 중 특정 대외활동에 지원한 지원자 목록
class CompanyActivityFormListView(generics.ListAPIView):
    serializer_class = CompanyActivityFormListSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        user = self.request.user.company_user
        activity_id = self.kwargs.get("activity_id")  # url에서 activity_id를 얻음
        return Activity.objects.filter(board__company_user=user, pk=activity_id)


# 지원관리/대외활동1/지원자1 : 지원자 한명의 지원서
class CompanyActivityFormDetailView(generics.RetrieveAPIView):
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        user = self.request.user.company_user
        activity_id = self.kwargs.get("activity_id")
        return Form.objects.filter(
            activity__pk=activity_id, activity__board__company_user=user
        )


# 지원관리/대외활동1/지원자1/합격 : 지원자 한명의 지원서 합격처리
class CompanyActivityFormConfirmView(generics.UpdateAPIView):
    queryset = Form.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        user = request.user.company_user
        form = self.get_object()
        if form.activity.board.company_user != user:
            return Response(
                {"detail": "해당 대외활동을 모집한 회사 유저만 합격처리가 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if form.accept_status != Form.PENDING:
            return Response(
                {"detail": "대기중인 지원서만 합격처리가 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        form.accept_status = Form.WAITING
        form.save()
        return Response(status=status.HTTP_200_OK)


# 지원관리/대외활동1/지원자1/불합격 : 지원자 한명의 지원서 불합격처리
class CompanyActivityFormRejectView(generics.UpdateAPIView):
    queryset = Form.objects.all()
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def update(self, request, *args, **kwargs):
        user = request.user.company_user
        form = self.get_object()
        if form.activity.board.company_user != user:
            return Response(
                {"detail": "해당 대외활동을 모집한 회사 유저만 불합격처리가 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        if form.accept_status != Form.PENDING:
            return Response(
                {"detail": "대기중인 지원서만 불합격처리가 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        form.accept_status = Form.REJECTED
        form.save()
        return Response(status=status.HTTP_200_OK)


# 지원관리/스크랩 : 스크랩 한 게시글 리스트
class ScrapBoardListView(generics.ListAPIView):
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        scraps = Scrap.objects.filter(student_user=self.request.user.student_user)
        return [scrap.board for scrap in scraps]


# 지원관리/스크랩/게시글 : 스크랩 한 게시글 하나
class ScrapBoardDetailView(generics.RetrieveAPIView):
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_object(self):
        board = Board.objects.get(pk=self.kwargs["pk"])

        if not Scrap.objects.filter(
            board=board, student_user=self.request.user.student_user
        ).exists():
            raise PermissionDenied("스크랩한 대상자가 아니므로 권한이 없습니다.")

        return board


# 대외활동 게시글/로그인 경우/스크랩 : 스크랩하기
class ScrapCreateView(generics.CreateAPIView):
    serializer_class = ScrapSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)


# 대외활동 게시글/로그인 경우/스크랩 : 스크랩취소
class ScrapDeleteView(generics.DestroyAPIView):
    queryset = Scrap.objects.all()
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_object(self):
        queryset = self.get_queryset()
        board = get_object_or_404(Board, pk=self.kwargs["board_pk"])
        obj = get_object_or_404(
            queryset, board=board, student_user=self.request.user.student_user
        )
        self.check_object_permissions(self.request, obj)
        return obj


# 지원 페이지/포트폴리오 있음 : 지원서 작성 화면
class FormFillView(generics.RetrieveAPIView):
    serializer_class = FormFillSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsProfileOwner,
    ]

    def get_queryset(self):
        user = self.request.user
        StudentUserProfile.objects.filter(student_user=user.student_user)


# 지원 페이지/포트폴리오 있음/지원서 제출하기 : 지원서 제출
class FormCreateView(generics.CreateAPIView):
    serializer_class = FormCreateSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def perform_create(self, serializer):
        selected_portfolio_id = self.request.data.get("student_user_portfolio")
        portfolio = StudentUserPortfolio.objects.get(id=selected_portfolio_id)
        serializer.save(
            student_user=self.request.user.student_user,
            student_user_portfolio=portfolio,
        )


# 지원관리/지원완료 : 지원서 제출한 게시물(대외활동) 리스트
class FormBoardListView(generics.ListAPIView):
    serializer_class = FormBoardListSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        forms = Form.objects.filter(
            student_user=self.request.user.student_user
        ).exclude(accept_status="accepted")
        return forms


# 대외활동 게시글/지원완료 : 지원서 제출한 게시물(대외활동) 하나
class FormBoardDetailView(generics.RetrieveAPIView):
    serializer_class = FormBoardDetailSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        forms = Form.objects.filter(
            student_user=self.request.user.student_user
        ).exclude(accept_status="accepted")
        return forms


# 제출완료 지원서 : 제출완료한 지원서
class FormDetailView(generics.RetrieveAPIView):
    serializer_class = FormDetailSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsFormOwner,
    ]

    def get_queryset(self):
        forms = Form.objects.filter(
            student_user=self.request.user.student_user
        ).exclude(accept_status="accepted")
        return forms


# 대외활동 게시글/확정대기/활동 최종 확정 : 합격한 대외활동 최종 활동 확정
class FormActivityAcceptView(generics.UpdateAPIView):
    queryset = Form.objects.all()
    permission_classes = [IsAuthenticated, IsStudentUser, IsFormOwner]

    def update(self, request, *args, **kwargs):
        form = self.get_object()
        if form.accept_status != Form.WAITING:
            return Response(
                {"detail": "합격한 활동에 대해서만 활동 최종 확정이 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        form.accept_status = Form.ACCEPTED
        form.save()
        AcceptedApplicant.objects.create(form=form)
        return Response(status=status.HTTP_200_OK)


# 대외활동 게시글/확정대기/활동 취소 : 합격한 대외활동 활동 취소
class FormActivityCancelView(generics.UpdateAPIView):
    queryset = Form.objects.all()
    permission_classes = [IsAuthenticated, IsStudentUser, IsFormOwner]

    def update(self, request, *args, **kwargs):
        form = self.get_object()
        if form.accept_status != Form.WAITING:
            return Response(
                {"detail": "합격한 활동에 대해서만 활동 취소가 가능합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        form.accept_status = Form.CANCELED
        form.save()
        return Response(status=status.HTTP_200_OK)


# 학생 프로필 검색
class CompanyStudentProfileListView(generics.ListAPIView):
    queryset = StudentUserProfile.objects.all()
    serializer_class = CompanyStudentProfileListSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]
    pagination_class = ProfileListPagination


# 학생 프로필 검색/프로필1
class CompanyStudentProfileDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyStudentProfileDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_object(self):
        profile_id = self.kwargs.get("profile_id")
        profile = StudentUserProfile.objects.get(pk=profile_id)
        return profile


# 학생 프로필 검색/프로필1/포트폴리오1
class CompanyStudentPortfolioDetailView(generics.RetrieveAPIView):
    serializer_class = CompanyStudentPortfolioDetailSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_queryset(self):
        profile_id = self.kwargs.get("profile_id")
        return StudentUserPortfolio.objects.filter(
            student_user__student_user_profile__pk=profile_id
        )


# 학생 프로필 검색/프로필1/지원제안 보내기
class CompanyStudentSuggestionCreateView(generics.CreateAPIView):
    serializer_class = SuggestionSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def create(self, request, *args, **kwargs):
        user = self.request.user
        company_user = CompanyUser.objects.get(user=user)

        if not company_user.board:
            return Response(
                {"detail": "적어도 하나의 대외활동 게시글을 작성해야 지원제안을 보낼 수 있습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )
        return super().create(request, *args, **kwargs)

    def perform_create(self, serializer):
        user = self.request.user
        company_user = CompanyUser.objects.get(user=user)
        profile_id = self.kwargs.get("profile_id")
        student_user = StudentUser.objects.get(student_user_profile__pk=profile_id)
        serializer.save(company_user=company_user, student_user=student_user)


# 포트폴리오/지원제안 : 들어온 지원제안
class SuggestionListView(generics.ListAPIView):
    serializer_class = SuggestionListSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        user = self.request.user.student_user
        suggestions = Suggestion.objects.order_by("-created_at").filter(
            student_user=user
        )
        return suggestions
