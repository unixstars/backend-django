from rest_framework import generics
from rest_framework.permissions import IsAuthenticated
from api.permissions import IsStudentUser, IsPortFolioOwner, IsProfileOwner
from .models import StudentUserPortfolio, StudentUserProfile
from .serializers import (
    StudentUserPortfolioSerializer,
    StudentUserPortfolioListSerializer,
    StudentUserProfileSerializer,
)


# 포트폴리오 추가: 학생 유저 포트폴리오 생성
class StudentUserPortFolioCreateView(generics.CreateAPIView):
    queryset = StudentUserPortfolio.objects.all()
    serializer_class = StudentUserPortfolioSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)


# 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 보기,수정,삭제
class StudentUserPortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentUserPortfolio.objects.all()
    serializer_class = StudentUserPortfolioSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsPortFolioOwner,
    ]


# 포트폴리오 : 학생 유저 포트폴리오 리스트
class StudentUserPortfolioListView(generics.ListAPIView):
    queryset = StudentUserPortfolio.objects.all()
    serializer_class = StudentUserPortfolioListSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsPortFolioOwner,
    ]


# 프로필/수정페이지 : 학생 유저 프로필 생성
class StudentUserProfileCreateView(generics.CreateAPIView):
    queryset = StudentUserProfile.objects.all()
    serializer_class = StudentUserProfileSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)


# 프로필 : 학생 유저 프로필 하나 보기,수정,삭제
class StudentUserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentUserProfile.objects.all()
    serializer_class = StudentUserProfileSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsProfileOwner,
    ]
