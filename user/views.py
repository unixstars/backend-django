from rest_framework import generics, parsers, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from api.permissions import IsStudentUser, IsPortFolioOwner, IsProfileOwner
from .models import StudentUserPortfolio, StudentUserProfile
from .serializers import (
    StudentUserPortfolioSerializer,
    StudentUserPortfolioUpdateSerializer,
    StudentUserPortfolioListSerializer,
    StudentUserProfileSerializer,
    StudentUserProfileUpdateSerializer,
)


# 포트폴리오 추가: 학생 유저 포트폴리오 생성
class StudentUserPortFolioCreateView(generics.CreateAPIView):
    queryset = StudentUserPortfolio.objects.all()
    serializer_class = StudentUserPortfolioSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)


# 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 보기,수정,삭제
class StudentUserPortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentUserPortfolio.objects.all()
    serializer_class = StudentUserPortfolioUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsPortFolioOwner,
    ]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]


# 포트폴리오 : 학생 유저 포트폴리오 리스트
class StudentUserPortfolioListView(generics.ListAPIView):
    serializer_class = StudentUserPortfolioListSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsPortFolioOwner,
    ]

    def get_queryset(self):
        user = self.request.user.student_user
        return StudentUserPortfolio.objects.filter(student_user=user)


# 프로필/수정페이지 : 학생 유저 프로필 생성
class StudentUserProfileCreateView(generics.CreateAPIView):
    queryset = StudentUserProfile.objects.all()
    serializer_class = StudentUserProfileSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)


# 프로필 : 학생 유저 프로필 하나 보기,수정,삭제
class StudentUserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentUserProfileUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsProfileOwner,
    ]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def get_object(self):
        try:
            student_user = self.request.user.student_user
            profile = StudentUserProfile.objects.get(student_user=student_user)
            return profile
        except StudentUserProfile.DoesNotExist:
            raise NotFound(detail="학생 프로필이 존재하지 않습니다.")


class CheckStudentUserProfileView(views.APIView):
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get(self, request, *args, **kwargs):
        student_user = request.user.student_user
        profile_exists = StudentUserProfile.objects.filter(
            student_user=student_user
        ).exists()
        return Response({"exists": profile_exists}, status=status.HTTP_200_OK)
