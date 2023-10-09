from django.urls import path
from .views import (
    CompanyVerificationView,
    CompanyManagerEmailSendView,
    CompanyManagerEmailVerificationView,
    CompanyManagerPhoneSendView,
    CompanyManagerPhoneVerificationView,
    CompanyUserRegisterView,
    UserLoginView,
    CompanyUserInfoFindPhoneSendView,
    CompanyUserInfoFindVerificationView,
    CompanyUserInfoPasswordChangeView,
    TestStudentRegisterView,
    TestCompanyUserRegisterView,
    GoogleLoginView,
    AppleLoginView,
    UserDeactivateView,
    KakaoLoginView,
    NaverLoginView,
)

urlpatterns = [
    path(
        # v 기업회원 회원가입 /법인 기업 인증 : 기업 인증
        "company/info/verify/",
        CompanyVerificationView.as_view(),
        name="company-info-verify",
    ),
    path(
        # v 기업회원 회원가입 /이메일인증 : 담당자 이메일 인증코드 전송
        "company/manager_email/send/",
        CompanyManagerEmailSendView.as_view(),
        name="company-manager_email-send",
    ),
    path(
        # v 기업회원 회원가입 /이메일인증 : 담당자 이메일 인증코드 확인
        "company/manager_email/verify/",
        CompanyManagerEmailVerificationView.as_view(),
        name="company-manager_email-verify",
    ),
    path(
        # v 기업회원 회원가입 /연락처 인증 : 담당자 휴대폰 인증번호 전송
        "company/manager_phone/send/",
        CompanyManagerPhoneSendView.as_view(),
        name="company-manager_phone-send",
    ),
    path(
        # v 기업회원 회원가입 /연락처 인증 :담당자 휴대폰 인증번호 확인
        "company/manager_phone/verify/",
        CompanyManagerPhoneVerificationView.as_view(),
        name="company-manager_phone-verify",
    ),
    path(
        # v 기업회원 회원가입 /회원가입 : 회원가입 실행
        "company/register/",
        CompanyUserRegisterView.as_view(),
        name="company-register",
    ),
    path(
        # v 기업회원 참여하기/로그인 : 학생/기업회원 로그인
        "login/",
        UserLoginView.as_view(),
        name="user-login",
    ),
    path(
        # v 테스트 학생 유저 가입
        "student/test/register/",
        TestStudentRegisterView.as_view(),
        name="student-test-register",
    ),
    path(
        "company/test/register/",
        TestCompanyUserRegisterView.as_view(),
        name="company-test-register",
    ),
    path(
        # v 찾기/휴대전화인증/인증코드 전송: 휴대전화 인증코드 전송 버튼
        "company/find/phone/send/",
        CompanyUserInfoFindPhoneSendView.as_view(),
        name="company-find-phone-send",
    ),
    path(
        # v 찾기/휴대전화인증/확인: 확인 버튼
        "company/find/phone/verify/",
        CompanyUserInfoFindVerificationView.as_view(),
        name="company-find-phone-verify",
    ),
    path(
        # v 정보 찾기 및 재설정: 비밀번호 변경
        "company/find/password/change/",
        CompanyUserInfoPasswordChangeView.as_view(),
        name="company-find-password-change",
    ),
    path(
        # 학생로그인/구글: 로그인 또는 회원가입
        "student/google/signin/",
        GoogleLoginView.as_view(),
        name="google-signin",
    ),
    path(
        # 학생로그인/애플: 로그인 또는 회원가입
        "student/apple/signin/",
        AppleLoginView.as_view(),
        name="apple-signin",
    ),
    path(
        # 학생로그인/카카오: 로그인 또는 회원가입
        "student/kakao/signin/",
        KakaoLoginView.as_view(),
        name="kakao-signin",
    ),
    path(
        # 학생로그인/네이버: 로그인 또는 회원가입
        "student/naver/signin/",
        NaverLoginView.as_view(),
        name="naver-signin",
    ),
    path(
        # v 회원탈퇴
        "deactivate/",
        UserDeactivateView.as_view(),
        name="user-deactive",
    ),
]
