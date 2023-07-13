from django.urls import path
from .views import (
    CompanyVerificationView,
    CompanyManagerEmailSendView,
    CompanyManagerEmailVerificationView,
    CompanyManagerPhoneSendView,
    CompanyManagerPhoneVerificationView,
    CompanyUserRegisterView,
)

urlpatterns = [
    path(
        "company/info/verify/",
        CompanyVerificationView.as_view(),
        name="company-info-verify",
    ),
    path(
        "company/manager_email/send/",
        CompanyManagerEmailSendView.as_view(),
        name="company-manager_email-send",
    ),
    path(
        "company/manager_email/verify/",
        CompanyManagerEmailVerificationView.as_view(),
        name="company-manager_email-verify",
    ),
    path(
        "company/manager_phone/send/",
        CompanyManagerPhoneSendView.as_view(),
        name="company-manager_phone-send",
    ),
    path(
        "company/manager_phone/verify/",
        CompanyManagerPhoneVerificationView.as_view(),
        name="company-manager_phone-verify",
    ),
    path(
        "company/register/",
        CompanyUserRegisterView.as_view(),
        name="company-register",
    ),
]
