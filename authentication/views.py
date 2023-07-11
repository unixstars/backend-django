"""
from user.models import User
from .serializers import (
    UserAuthSerializer,
    GeneralUserAuthSerializer,
    CompanyUserAuthSerializer,
    RefreshTokenSerializer,
)
from rest_framework import generics, status
from rest_framework.permissions import AllowAny
from rest_framework.response import Response
from django.contrib.auth import authenticate
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.exceptions import TokenError


class GeneralRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = GeneralUserAuthSerializer
    permission_classes = (AllowAny,)


class CompanyRegisterView(generics.CreateAPIView):
    queryset = User.objects.all()
    serializer_class = CompanyUserAuthSerializer
    permission_classes = (AllowAny,)


class LoginView(generics.GenericAPIView):
    serializer_class = UserAuthSerializer
    permission_classes = (AllowAny,)

    # JWT 토큰을 사용하는 로그인 로직
    def post(self, request, *args, **kwargs):
        email = request.data.get("email")
        password = request.data.get("password")
        user = authenticate(request, email=email, password=password)

        if user is not None:
            # 로그인 로직 구현 - JWT 토큰 사용
            refresh = RefreshToken.for_user(user)
            access_token = str(refresh.access_token)

            return Response(
                {
                    "access_token": access_token,
                    "refresh_token": str(refresh),
                },
                status=status.HTTP_200_OK,
            )
        else:
            return Response({"detail": "로그인 실패!"}, status=status.HTTP_401_UNAUTHORIZED)


class TokenRefreshView(generics.GenericAPIView):
    serializer_class = RefreshTokenSerializer
    permission_classes = (AllowAny,)

    def post(self, request, *args, **kwargs):
        refresh_token = request.data.get("refresh_token")

        if refresh_token is None:
            return Response(
                {"error": "Refresh token이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            token = RefreshToken(refresh_token)
            access_token = str(token.access_token)

            return Response(
                {
                    "access_token": access_token,
                },
                status=status.HTTP_200_OK,
            )
        except TokenError:
            return Response(
                {"error": "잘못된 Refresh token입니다."}, status=status.HTTP_401_UNAUTHORIZED
            )
"""
from user.models import CompanyUser
from .serializers import CompanyUserSerializer
from rest_framework import generics


# Test
class CompanyUserView(generics.GenericAPIView):
    queryset = CompanyUser.objects.all()
    serializer_class = CompanyUserSerializer
