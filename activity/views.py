from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from rest_framework.exceptions import PermissionDenied
from .models import Board, Scrap, Form
from .paginations import BoardListPagination
from user.models import CompanyUser
from .serializers import (
    BoardListSerializer,
    BoardCreateSerializer,
    BoardDetailSerializer,
    ScrapSerializer,
    FormSerializer,
)
from api.permissions import (
    IsCompanyUser,
    IsStudentUser,
    IsBoardOwner,
)
from django.db.models import F
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta
from django.shortcuts import get_object_or_404


class BoardListView(generics.ListAPIView):
    queryset = Board.objects.order_by("-views", "-created_at").all()
    serializer_class = BoardListSerializer
    permission_classes = [AllowAny]
    pagination_class = BoardListPagination


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


class BoardCreateView(generics.CreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardCreateSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def perform_create(self, serializer):
        company_user = CompanyUser.objects.get(user=self.request.user)
        serializer.save(company_user=company_user)


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

        board.is_expired = False
        board.duration_extended += 1
        board.save()

        return Response(status=status.HTTP_200_OK)


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


class ScrapListView(generics.ListAPIView):
    serializer_class = BoardListSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        scraps = Scrap.objects.filter(student_user=self.request.user.student_user)
        return [scrap.board for scrap in scraps]


class ScrapDetailView(generics.RetrieveAPIView):
    serializer_class = BoardDetailSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_object(self):
        board = Board.objects.get(pk=self.kwargs["pk"])

        if not Scrap.objects.filter(
            board=board, student_user=self.request.user.student_user
        ).exists():
            raise PermissionDenied("스크랩한 대상자가 아니므로 권한이 없습니다.")

        return board


class ScrapCreateView(generics.CreateAPIView):
    serializer_class = ScrapSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)


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


class FormListView(generics.ListAPIView):
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get_queryset(self):
        return Form.objects.filter(student_user=self.request.user.student_user)


class FormDetailView(generics.RetrieveAPIView):
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]
    lookup_field = "id"

    def get_queryset(self):
        return Form.objects.filter(student_user=self.request.user.student_user)


class FormCreateView(generics.CreateAPIView):
    serializer_class = FormSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)
