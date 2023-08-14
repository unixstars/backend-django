from django.urls import path
from .views import (
    StudentUserProfileCreateView,
    StudentUserProfileDetailView,
    StudentUserPortFolioCreateView,
    StudentUserPortfolioDetailView,
    StudentUserPortfolioListView,
)

urlpatterns = [
    # v 프로필/수정페이지 : 학생 유저 프로필 생성
    path(
        "student/profile/create/",
        StudentUserProfileCreateView.as_view(),
        name="student-profile-create",
    ),
    # v 프로필 : 학생 유저 프로필 하나 보기
    path(
        # GET
        "student/profile/<int:pk>/",
        StudentUserProfileDetailView.as_view(),
        name="student-profile-detail",
    ),
    # v 프로필 : 학생 유저 프로필 하나 수정
    path(
        # PUT
        "student/profile/<int:pk>/update/",
        StudentUserProfileDetailView.as_view(),
        name="student-profile-update",
    ),
    # v 프로필 : 학생 유저 프로필 하나 삭제
    path(
        # DELETE
        "student/profile/<int:pk>/delete/",
        StudentUserProfileDetailView.as_view(),
        name="student-profile-delete",
    ),
    # 포트폴리오 추가: 학생 유저 포트폴리오 생성
    path(
        "student/portfolio/create/",
        StudentUserPortFolioCreateView.as_view(),
        name="student-portfolio-create",
    ),
    # 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 보기
    path(
        # GET
        "student/portfolio/<int:pk>/",
        StudentUserPortfolioDetailView.as_view(),
        name="student-portfolio-detail",
    ),
    # 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 수정
    path(
        # PUT
        "student/portfolio/<int:pk>/update/",
        StudentUserPortfolioDetailView.as_view(),
        name="student-portfolio-update",
    ),
    # 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 삭제
    path(
        # DELETE
        "student/portfolio/<int:pk>/delete/",
        StudentUserPortfolioDetailView.as_view(),
        name="student-portfolio-delete",
    ),
    # 포트폴리오 : 학생 유저 포트폴리오 리스트
    path(
        "student/portfolio/",
        StudentUserPortfolioListView.as_view(),
        name="student-portfolio-list",
    ),
]
