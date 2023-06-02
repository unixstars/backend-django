from django.urls import path
from .views import GeneralRegisterView, CompanyRegisterView, LoginView, TokenRefreshView

urlpatterns = [
    path("register/general/", GeneralRegisterView.as_view(), name="general_register"),
    path("register/company/", CompanyRegisterView.as_view(), name="company_register"),
    path("login/", LoginView.as_view(), name="login"),
    path("refresh_token/", TokenRefreshView.as_view(), name="refresh_token"),
]
