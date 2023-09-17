from django.urls import path
from .views import (
    StudentUserProfileCreateView,
    StudentUserProfileDetailView,
    StudentUserPortFolioCreateView,
    StudentUserPortfolioDetailView,
    StudentUserPortfolioListView,
    CheckStudentUserProfileView,
    StudentBankAccountCheckView,
    CompanyUserInfoView,
    CompanyUserInfoAuthView,
    CompanyUserInfoChangePhoneSendView,
    CompanyUserInfoChangePhoneVerificationView,
    CompanyUserInfoChangeView,
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
        "student/profile/",
        StudentUserProfileDetailView.as_view(),
        name="student-profile-detail",
    ),
    # v 프로필 : 학생 유저 프로필 하나 수정
    path(
        # PUT
        "student/profile/update/",
        StudentUserProfileDetailView.as_view(),
        name="student-profile-update",
    ),
    # v 프로필 : 학생 유저 프로필 하나 삭제
    path(
        # DELETE
        "student/profile/delete/",
        StudentUserProfileDetailView.as_view(),
        name="student-profile-delete",
    ),
    # v 포트폴리오 추가: 학생 유저 포트폴리오 생성
    path(
        "student/portfolio/create/",
        StudentUserPortFolioCreateView.as_view(),
        name="student-portfolio-create",
    ),
    # v 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 보기
    path(
        # GET
        "student/portfolio/<int:pk>/",
        StudentUserPortfolioDetailView.as_view(),
        name="student-portfolio-detail",
    ),
    # v 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 수정
    path(
        # PUT
        "student/portfolio/<int:pk>/update/",
        StudentUserPortfolioDetailView.as_view(),
        name="student-portfolio-update",
    ),
    # v 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 삭제
    path(
        # DELETE
        "student/portfolio/<int:pk>/delete/",
        StudentUserPortfolioDetailView.as_view(),
        name="student-portfolio-delete",
    ),
    # v 포트폴리오 : 학생 유저 포트폴리오 리스트
    path(
        "student/portfolio/",
        StudentUserPortfolioListView.as_view(),
        name="student-portfolio-list",
    ),
    # v 학생 프로필 존재 여부
    path(
        "student/profile/exists/",
        CheckStudentUserProfileView.as_view(),
        name="student-profile-check",
    ),
    # 프로필/수정페이지/계좌인증
    path(
        "student/profile/bank/check/",
        StudentBankAccountCheckView.as_view(),
        name="student-bank-check",
    ),
    # 내 정보/기업회원
    path(
        "company/info/",
        CompanyUserInfoView.as_view(),
        name="company-info",
    ),
    # 회원정보 변경 인증(비밀번호)
    path(
        "company/info/change/auth/",
        CompanyUserInfoAuthView.as_view(),
        name="company-info-change-auth",
    ),
    # 회원정보 /비밀번호 변경:담당자 연락처 인증번호 전송
    path(
        "company/info/change/phone/send/",
        CompanyUserInfoChangePhoneSendView.as_view(),
        name="company-info-change-phone-send",
    ),
    # 회원정보 /비밀번호 변경:담당자 연락처 인증번호 인증
    path(
        "company/info/change/phone/verify/",
        CompanyUserInfoChangePhoneVerificationView.as_view(),
        name="company-info-change-phone-verifiy",
    ),
    # 회원정보/비밀번호 변경: 회원정보/비밀번호 변경 버튼
    path(
        "company/info/change/",
        CompanyUserInfoChangeView.as_view(),
        name="company-info-change",
    ),
]
