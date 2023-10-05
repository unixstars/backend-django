from rest_framework import views, status, generics
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from django.core.cache import cache
import requests, os, random, jwt, json
from api.utils import hash_function
from .utils import SendRateThrottle, LoginRateThrottle
from .serializers import (
    CompanyVerificationSerializer,
    CompanyManagerEmailVerificationSerializer,
    CompanyManagerPhoneVerificationSerializer,
    CompanyUserRegistrationSerializer,
    TestStudentRegisterSerializer,
    CompanyUserInfoFindVerificationSerializer,
    UserDeactivateSerializer,
)
from .ncloud import get_api_keys
from dj_rest_auth.registration.views import RegisterView
from rest_framework.permissions import AllowAny

from django.utils.translation import gettext_lazy as _
from dj_rest_auth.views import LoginView, PasswordChangeView

from rest_framework_simplejwt.tokens import RefreshToken
from user.models import User, StudentUser, CompanyUser
from google.oauth2 import id_token
from google.auth.transport import requests as google_requests


# 기업회원 회원가입/법인 기업 인증 : 법인 인증
class CompanyVerificationView(views.APIView):
    serializer_class = CompanyVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        url = "https://api.odcloud.kr/api/nts-businessman/v1"
        service_key = os.getenv("BUSINESS_SERVICE_KEY")
        business_number = serializer.validated_data.get("business_number")

        if CompanyUser.objects.filter(business_number=business_number).exists():
            return Response({"detail": "이미 등록된 사업자 번호입니다."}, status=400)

        try:
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


# 기업회원 회원가입/이메일 인증 : 담당자 이메일 전송
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


# 기업회원 회원가입/이메일 인증 : 담당자 이메일 인증
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


# 기업회원 회원가입/연락처 인증 : 담당자 연락처 전송
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


# 기업회원 회원가입/연락처 인증 : 담당자 연락처 인증
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


# 기업회원 회원가입/회원가입 : 기업회원 회원가입
class CompanyUserRegisterView(RegisterView):
    serializer_class = CompanyUserRegistrationSerializer
    permission_classes = [AllowAny]


# 기업회원 참여하기/로그인 : 기업회원 로그인
class UserLoginView(LoginView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]
    throttle_field = "email"


# 테스트 학생 유저 가입
class TestStudentRegisterView(RegisterView):
    serializer_class = TestStudentRegisterSerializer
    permission_classes = [AllowAny]


# 찾기/휴대전화인증/인증코드 전송: 휴대전화 인증코드 전송 버튼
class CompanyUserInfoFindPhoneSendView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [SendRateThrottle]
    throttle_field = "register_phone"

    def post(self, request):
        register_phone = request.data.get("register_phone")
        register_phone_auth_number = random.randint(100000, 999999)
        cache.set(hash_function(register_phone), register_phone_auth_number, 60 * 5)

        try:
            CompanyUser.objects.get(manager_phone=register_phone)
        except CompanyUser.DoesNotExist:
            return Response({"detail": "등록 번호와 일치하는 기업 유저가 존재하지 않습니다."}, status=400)

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
                "subject": "[유니스타 기업회원정보 찾기 인증]",
                "content": f"유니스타 기업회원정보 찾기 인증번호는 [{register_phone_auth_number}]입니다. 인증번호를 정확히 입력해주세요.",
                "messages": [{"to": f"{register_phone}"}],
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


# 찾기/휴대전화인증/확인: 확인 버튼
class CompanyUserInfoFindVerificationView(views.APIView):
    serializer_class = CompanyUserInfoFindVerificationSerializer
    permission_classes = [AllowAny]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        register_phone = serializer.validated_data.get("register_phone")
        auth_number = serializer.validated_data.get("auth_number")

        correct_auth_number = cache.get(hash_function(register_phone))

        if correct_auth_number is None:
            return Response({"detail": "인증번호가 만료되었습니다."}, status=400)
        elif correct_auth_number != auth_number:
            return Response({"detail": "잘못된 인증번호 입니다."}, status=400)
        else:
            # 인증여부 및 등록 번호 캐시에 추가(비밀번호 변경에 활용)
            cache.set(
                hash_function(register_phone) + "_authenticated",
                register_phone,
                60 * 60,
            )
            company_user = CompanyUser.objects.get(manager_phone=register_phone)
            email = company_user.user.email
            return Response(
                {
                    "detail": "인증에 성공하였습니다.",
                    "register_phone": f"{register_phone}",
                    "email": f"{email}",
                }
            )


# 정보 찾기 및 재설정: 비밀번호 변경
class CompanyUserInfoPasswordChangeView(PasswordChangeView):
    permission_classes = [AllowAny]

    def post(self, request, *args, **kwargs):
        # 캐시에서 인증된 전화번호 가져오기
        authenticated_phone = cache.get(
            hash_function(request.data.get("register_phone")) + "_authenticated"
        )

        if not authenticated_phone:
            return Response(
                {"error": "전화번호가 인증되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 인증된 전화번호를 가진 회사 사용자 찾기
        try:
            company_user = CompanyUser.objects.get(manager_phone=authenticated_phone)
            user = company_user.user
        except CompanyUser.DoesNotExist:
            return Response(
                {"error": "해당 전화번호를 가진 회사 사용자를 찾을 수 없습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # user의 request.user를 인증된 회사 사용자로 설정(PasswordChangeView의 기본 유저를 바꾸기)
        request.user = user

        # 원래 PasswordChangeView의 post 메서드 호출
        return super().post(request, *args, **kwargs)


# 구글 로그인/회원가입
class GoogleLoginView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        access_token_str = request.data.get("accessToken", None)

        if access_token_str is None:
            return Response(
                {"error": "accessToken이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # Google의 OAuth2 엔드포인트를 사용하여 유저 정보를 가져옵니다
        try:
            response = requests.get(
                "https://www.googleapis.com/oauth2/v3/tokeninfo",
                params={"access_token": access_token_str},
            )
            payload = response.json()
        except Exception as e:
            return Response({"error": str(e)}, status=status.HTTP_400_BAD_REQUEST)

        if "email" not in payload:
            return Response(
                {"error": "유효하지 않은 accessToken 입니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        email = payload["email"]

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return Response(
                    {"error": "회원탈퇴한 유저입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            user = User.objects.create(email=email)
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

        refresh = RefreshToken.for_user(user)
        token_data = {
            "access": str(refresh.access_token),
            "refresh": str(refresh),
        }

        return Response(token_data)


# 애플 로그인/회원가입
class AppleLoginView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        id_token = request.data.get("idToken", None)
        if id_token is None:
            return Response(
                {"error": "idToken이 필요합니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        # 애플의 공개키 가져오기
        url = f"https://appleid.apple.com/auth/keys"
        try:
            response = requests.get(url)
            response.raise_for_status()
            key_data = response.json()["keys"]
        except requests.exceptions.HTTPError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        # idToken 검증을 위해 헤더로부터 값 가져오기
        header = jwt.get_unverified_header(id_token)
        kid = header["kid"]

        # idToken의 헤더 값이 존재하는지 검증
        apple_key = next((key for key in key_data if key["kid"] == kid), None)
        if not apple_key:
            return Response(
                {"error": "유효하지 않은 key ID 입니다."}, status=status.HTTP_400_BAD_REQUEST
            )

        # 공개키로부터 idToken 복호화 및 검증
        public_key = jwt.algorithms.RSAAlgorithm.from_jwk(json.dumps(apple_key))

        try:
            payload = jwt.decode(
                id_token,
                public_key,
                algorithms=["RS256"],
                audience=os.getenv("APPLE_CLIENT_ID"),
            )
        except jwt.exceptions.InvalidTokenError as err:
            return Response({"error": str(err)}, status=status.HTTP_400_BAD_REQUEST)

        email = payload.get("email", None)
        client_id = payload.get("sub", None)

        if not email or not client_id:
            return Response(
                {"error": "이메일이나 Cleint ID가 Provider로부터 제공되지 않았습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        try:
            user = User.objects.get(email=email)
            if not user.is_active:
                return Response(
                    {"error": "회원탈퇴한 유저입니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )
        except User.DoesNotExist:
            user = User.objects.create(email=email)
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

        refresh = RefreshToken.for_user(user)
        token_data = {"access": str(refresh.access_token), "refresh": str(refresh)}

        return Response(token_data)


# 카카오 로그인/회원가입 => 프론트 작업 후 수정 예정
class KakaoLoginView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        access_token = request.data.get("accessToken", None)
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
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(email=email)
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {"access": str(refresh.access_token), "refresh": str(refresh)}
        )
        return response


# 네이버 로그인/회원가입 => 프론트 작업 후 수정 예정
class NaverLoginView(views.APIView):
    permission_classes = [AllowAny]
    throttle_classes = [LoginRateThrottle]

    def post(self, request):
        access_token = request.data.get("accessToken", None)
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
            user = User.objects.get(email=email)
        except User.DoesNotExist:
            user = User.objects.create(email=email)
            student_user = StudentUser.objects.create(user=user)
            student_user.save()

        refresh = RefreshToken.for_user(user)

        response = Response(
            {"access": str(refresh.access_token), "refresh": str(refresh)}
        )
        return response


# 회원탈퇴
class UserDeactivateView(generics.GenericAPIView):
    serializer_class = UserDeactivateSerializer
    permission_classes = [IsAuthenticated]

    def post(self, request):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        request.user.is_active = False
        request.user.save()
        return Response({"message": "회원탈퇴가 완료되었습니다."}, status=status.HTTP_200_OK)
