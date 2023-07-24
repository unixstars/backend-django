from rest_framework import generics, status
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import Board
from .paginations import BoardListPagination
from user.models import CompanyUser
from .serializers import (
    BoardListSerializer,
    BoardCreateSerializer,
    BoardDetailSerializer,
)
from api.permissions import IsCompanyUser, IsBoardOwner
from django.db.models import F
from rest_framework.response import Response
from django.utils import timezone
from datetime import timedelta


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

        if original_deadline > timezone.now():
            board.duration += timedelta(days=7)
        else:
            board.duration = timezone.now() - board.created_at + timedelta(days=7)

        board.is_expired = False
        board.save()

        return Response(status=status.HTTP_200_OK)
