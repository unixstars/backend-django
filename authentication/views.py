from rest_framework import views, status
from rest_framework.response import Response
from django.core.cache import cache
import requests, os, random, jwt, json
from api.utils import hash_function
from .utils import SendRateThrottle, LoginRateThrottle
from .serializers import (
    CompanyVerificationSerializer,
    CompanyManagerEmailVerificationSerializer,
    CompanyManagerPhoneVerificationSerializer,
    CompanyUserRegistrationSerializer,
)
from .ncloud import get_api_keys
from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny

from dj_rest_auth.app_settings import api_settings
from allauth.account import app_settings as allauth_account_settings
from django.conf import settings
from django.utils.translation import gettext_lazy as _
from dj_rest_auth.views import LoginView

from rest_framework_simplejwt.tokens import RefreshToken
from user.models import User, StudentUser
from jwt.algorithms import RSAAlgorithm


class CompanyVerificationView(views.APIView):
    serializer_class = CompanyVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        try:
            url = "https://api.odcloud.kr/api/nts-businessman/v1"
            service_key = os.getenv("BUSINESS_SERVICE_KEY")
            business_number = serializer.validated_data.get("business_number")

            # 사업자등록 상태조회 API
            response_b_status = requests.post(
                f"{url}/status?serviceKey={service_key}",
                json={"b_no": [business_number]},
            )
            response_b_status.raise_for_status()

            data_b_status = response_b_status.json()
            item_b_status = data_b_status["data"][0]
            if not item_b_status["b_stt"] == "계속사업자":
                return Response({"detail": "기업 정보가 유효하지 않습니다. 계속사업자가 아님."}, status=400)

            # 사업자등록 진위여부 API
            data = {
                "businesses": [
                    {
                        "b_no": business_number,
                        "start_dt": serializer.validated_data.get(
                            "start_date"
                        ).strftime("%Y%m%d"),
                        "p_nm": serializer.validated_data.get("ceo_name"),
                        "p_nm_2": "",
                        "b_nm": "",
                        "corp_no": serializer.validated_data.get("corporate_number"),
                        "b_sector": "",
                        "b_type": "",
                        "b_adr": "",
                    }
                ]
            }

            response = requests.post(
                f"{url}/validate?serviceKey={service_key}",
                json=data,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            return Response({"detail": str(err)}, status=response.status_code)

        data = response.json()
        item = data["data"][0]
        if not item["valid"] == "01":
            return Response({"detail": "기업 정보가 유효하지 않습니다."}, status=400)

        cache.set(hash_function(business_number) + "_authenticated", True, 60 * 60)
        return Response(data)


class CompanyManagerEmailSendView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SendRateThrottle]
    throttle_field = "manager_email"

    def post(self, request):
        manager_email = request.data.get("manager_email")
        manager_email_auth_code = random.randint(100000, 999999)
        cache.set(hash_function(manager_email), manager_email_auth_code, 60 * 5)

        try:
            uri = "/api/v1/mails"
            timestamp, access_key, signing_key = get_api_keys(uri, "POST")

            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "x-ncp-apigw-timestamp": timestamp,
                "x-ncp-iam-access-key": access_key,
                "x-ncp-apigw-signature-v2": signing_key,
            }

            data = {
                "senderAddress": os.getenv("EMAIL_SENDER_ADDRESS"),
                "title": "유니스타 기업회원가입 인증 메일",
                "body": f"유니스타 기업회원 메일 인증 코드는 {manager_email_auth_code}입니다. 인증코드를 정확히 입력해 주세요.",
                "recipients": [
                    {
                        "address": f"{manager_email}",
                        "type": "R",
                    }
                ],
                "individual": True,
                "advertising": False,
            }

            response = requests.post(
                f"https://mail.apigw.ntruss.com{uri}",
                headers=headers,
                json=data,
            )
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            if response.status_code != 201:
                return Response({"detail": str(err)}, status=response.status_code)

        return Response(response.json())


class CompanyManagerEmailVerificationView(views.APIView):
    serializer_class = CompanyManagerEmailVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager_email = serializer.validated_data.get("manager_email")
        auth_code = serializer.validated_data.get("auth_code")

        correct_auth_code = cache.get(hash_function(manager_email))

        if correct_auth_code is None:
            return Response({"detail": "인증코드가 만료되었습니다."}, status=400)
        elif correct_auth_code != auth_code:
            return Response({"detail": "잘못된 인증코드 입니다."}, status=400)
        else:
            # 인증여부 캐시에 추가(최종 회원가입에 활용)
            cache.set(hash_function(manager_email) + "_authenticated", True, 60 * 60)
            return Response({"detail": "인증에 성공하였습니다."})


class CompanyManagerPhoneSendView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SendRateThrottle]
    throttle_field = "manager_phone"

    def post(self, request):
        manager_phone = request.data.get("manager_phone")
        manager_phone_auth_number = random.randint(100000, 999999)
        cache.set(hash_function(manager_phone), manager_phone_auth_number, 60 * 5)

        # 네이버 클라우드 SMS API
        try:
            service_id = os.getenv("SMS_SERVICE_ID")
            uri = f"/sms/v2/services/{service_id}/messages"
            timestamp, access_key, signing_key = get_api_keys(uri, "POST")

            headers = {
                "Content-Type": "application/json; charset=utf-8",
                "x-ncp-apigw-timestamp": timestamp,
                "x-ncp-iam-access-key": access_key,
                "x-ncp-apigw-signature-v2": signing_key,
            }

            data = {
                "type": "SMS",
                "contentType": "COMM",
                "from": os.getenv("SMS_CALLING_NUM"),
                "subject": "[유니스타 기업회원가입 담당자 인증]",
                "content": f"유니스타 기업회원가입 인증번호는 [{manager_phone_auth_number}]입니다. 인증번호를 정확히 입력해주세요.",
                "messages": [{"to": f"{manager_phone}"}],
            }

            response = requests.post(
                f"https://sens.apigw.ntruss.com{uri}",
                headers=headers,
                json=data,
            )
            response.raise_for_status()

        except requests.exceptions.HTTPError as err:
            if response.status_code != 202:
                return Response({"detail": str(err)}, status=response.status_code)

        return Response(response.json())


class CompanyManagerPhoneVerificationView(views.APIView):
    serializer_class = CompanyManagerPhoneVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        manager_phone = serializer.validated_data.get("manager_phone")
        auth_number = serializer.validated_data.get("auth_number")

        correct_auth_number = cache.get(hash_function(manager_phone))

        if correct_auth_number is None:
            return Response({"detail": "인증번호가 만료되었습니다."}, status=400)
        elif correct_auth_number != auth_number:
            return Response({"detail": "잘못된 인증번호 입니다."}, status=400)
        else:
            # 인증여부 캐시에 추가(최종 회원가입에 활용)
            cache.set(hash_function(manager_phone) + "_authenticated", True, 60 * 60)
            return Response({"detail": "인증에 성공하였습니다."})


class CompanyUserRegisterView(RegisterView):
    serializer_class = CompanyUserRegistrationSerializer
    permission_classes = [AllowAny]
    """
    def get_response_data(self, user):
        if (
            allauth_account_settings.EMAIL_VERIFICATION
            == allauth_account_settings.EmailVerificationMethod.MANDATORY
        ):
            return {"detail": _("Verification e-mail sent.")}

        if api_settings.USE_JWT:
            data = {
                "user": user,
                "access": self.access_token,
                "refresh": "",
            }

            # Create an instance of the response to set the cookie
            response = Response(
                api_settings.JWT_SERIALIZER(
                    data, context=self.get_serializer_context()
                ).data
            )

            # Set the refresh token in an HTTP only cookie
            response.set_cookie(
                key="refresh",
                value=self.refresh_token,
                httponly=True,
                secure=settings.CSRF_COOKIE_SECURE,
            )

            return response
        elif api_settings.SESSION_LOGIN:
            return None
        else:
            return api_settings.TOKEN_SERIALIZER(
                user.auth_token, context=self.get_serializer_context()
            ).data

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        user = self.perform_create(serializer)
        headers = self.get_success_headers(serializer.data)
        response = self.get_response_data(user)

        if isinstance(response, Response):
            return response
        elif response:
            return Response(
                response,
                status=status.HTTP_201_CREATED,
                headers=headers,
            )
        else:
            return Response(status=status.HTTP_204_NO_CONTENT, headers=headers)
        """


class UserLoginView(LoginView):
    throttle_classes = [LoginRateThrottle]
    throttle_field = "email"


class GoogleLoginView(views.APIView):
    def post(self, request):
        access_token = request.data.get("access_token", None)
        if access_token is None:
            return Response(
                {"error": "Access token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://www.googleapis.com/oauth2/v1/tokeninfo?access_token={access_token}"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        data = response.json()
        email = data.get("email", None)
        client_id = data.get(
            "user_id", None
        )  # Note: Google uses 'user_id' instead of 'id'

        if not email or not client_id:
            return Response(
                {"error": "Email or client_id missing from provider"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email, username=client_id)
        except User.DoesNotExist:
            user = User.objects.create(email=email, username=client_id)
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "access": str(refresh.access_token),
            }
        )
        response.set_cookie(key="refresh", value=str(refresh), httponly=True)
        return response


class AppleLoginView(views.APIView):
    def post(self, request):
        access_token = request.data.get("access_token", None)
        if access_token is None:
            return Response(
                {"error": "Access token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        url = f"https://appleid.apple.com/auth/keys"
        try:
            response = requests.get(url)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        data = response.json()
        public_key_data = data["keys"][0]
        public_key = RSAAlgorithm.from_jwk(json.dumps(public_key_data))

        try:
            payload = jwt.decode(
                access_token, public_key, algorithms=["RS256"], audience="YOUR_AUDIENCE"
            )
        except jwt.exceptions.InvalidTokenError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        email = payload.get("email", None)
        client_id = payload.get("sub", None)

        if not email or not client_id:
            return Response(
                {"error": "Email or client_id missing from provider"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email, username=client_id)
        except User.DoesNotExist:
            user = User.objects.create(email=email, username=client_id)
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "access": str(refresh.access_token),
            }
        )
        response.set_cookie(key="refresh", value=str(refresh), httponly=True)
        return response


class KakaoLoginView(views.APIView):
    def post(self, request):
        access_token = request.data.get("access_token", None)
        if access_token is None:
            return Response(
                {"error": "Access token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {
            "Authorization": f"Bearer {access_token}",
            "Content-type": "application/x-www-form-urlencoded;charset=utf-8",
        }
        url = "https://kapi.kakao.com/v2/user/me"

        try:
            response = requests.post(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        data = response.json()
        email = data.get("kakao_account", {}).get("email", None)
        client_id = data.get("id", None)

        if not email or not client_id:
            return Response(
                {"error": "Email or client_id missing from provider"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email, username=str(client_id))
        except User.DoesNotExist:
            user = User.objects.create(email=email, username=str(client_id))
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "access": str(refresh.access_token),
            }
        )
        response.set_cookie(key="refresh", value=str(refresh), httponly=True)
        return response


class NaverLoginView(views.APIView):
    def post(self, request):
        access_token = request.data.get("access_token", None)
        if access_token is None:
            return Response(
                {"error": "Access token is required"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        headers = {"Authorization": f"Bearer {access_token}"}
        url = "https://openapi.naver.com/v1/nid/me"

        try:
            response = requests.get(url, headers=headers)
            response.raise_for_status()
        except requests.exceptions.HTTPError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        data = response.json()
        email = data.get("response", {}).get("email", None)
        client_id = data.get("response", {}).get("id", None)

        if not email or not client_id:
            return Response(
                {"error": "Email or client_id missing from provider"},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email, username=str(client_id))
        except User.DoesNotExist:
            user = User.objects.create(email=email, username=str(client_id))
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {
                "access": str(refresh.access_token),
            }
        )
        response.set_cookie(key="refresh", value=str(refresh), httponly=True)
        return response
