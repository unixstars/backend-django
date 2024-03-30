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
    ##학생
    # 학생로그인/구글: 로그인 또는 회원가입
    path(
        "student/google/signin/",
        GoogleLoginView.as_view(),
        name="google-signin",
    ),
    # 학생로그인/애플: 로그인 또는 회원가입
    path(
        "student/apple/signin/",
        AppleLoginView.as_view(),
        name="apple-signin",
    ),
    # 학생로그인/카카오: 로그인 또는 회원가입
    path(
        "student/kakao/signin/",
        KakaoLoginView.as_view(),
        name="kakao-signin",
    ),
    # 학생로그인/네이버: 로그인 또는 회원가입
    path(
        "student/naver/signin/",
        NaverLoginView.as_view(),
        name="naver-signin",
    ),
    # 테스트 학생 유저 가입
    path(
        "student/test/register/",
        TestStudentRegisterView.as_view(),
        name="student-test-register",
    ),
    ##기업
    # 기업회원 회원가입 /법인 기업 인증 : 기업 인증
    path(
        "company/info/verify/",
        CompanyVerificationView.as_view(),
        name="company-info-verify",
    ),
    # 기업회원 회원가입 /이메일인증 : 담당자 이메일 인증코드 전송
    path(
        "company/manager_email/send/",
        CompanyManagerEmailSendView.as_view(),
        name="company-manager_email-send",
    ),
    # 기업회원 회원가입 /이메일인증 : 담당자 이메일 인증코드 확인
    path(
        "company/manager_email/verify/",
        CompanyManagerEmailVerificationView.as_view(),
        name="company-manager_email-verify",
    ),
    # 기업회원 회원가입 /연락처 인증 : 담당자 휴대폰 인증번호 전송
    path(
        "company/manager_phone/send/",
        CompanyManagerPhoneSendView.as_view(),
        name="company-manager_phone-send",
    ),
    # 기업회원 회원가입 /연락처 인증 :담당자 휴대폰 인증번호 확인
    path(
        "company/manager_phone/verify/",
        CompanyManagerPhoneVerificationView.as_view(),
        name="company-manager_phone-verify",
    ),
    # 기업회원 회원가입 /회원가입 : 회원가입 실행
    path(
        "company/register/",
        CompanyUserRegisterView.as_view(),
        name="company-register",
    ),
    # 찾기/휴대전화인증/인증코드 전송: 휴대전화 인증코드 전송 버튼
    path(
        "company/find/phone/send/",
        CompanyUserInfoFindPhoneSendView.as_view(),
        name="company-find-phone-send",
    ),
    # 찾기/휴대전화인증/확인: 확인 버튼
    path(
        "company/find/phone/verify/",
        CompanyUserInfoFindVerificationView.as_view(),
        name="company-find-phone-verify",
    ),
    # 정보 찾기 및 재설정: 비밀번호 변경
    path(
        "company/find/password/change/",
        CompanyUserInfoPasswordChangeView.as_view(),
        name="company-find-password-change",
    ),
    # 테스트 기업 유저 가입
    path(
        "company/test/register/",
        TestCompanyUserRegisterView.as_view(),
        name="company-test-register",
    ),
    ## 공통
    # 로그인
    path(
        "login/",
        UserLoginView.as_view(),
        name="user-login",
    ),
    # 회원탈퇴
    path(
        "deactivate/",
        UserDeactivateView.as_view(),
        name="user-deactive",
    ),
]
