from rest_framework import views
from rest_framework.response import Response
from django.core.cache import cache
import requests, os, random
from api.common import hash_function
from .serializers import (
    CompanyVerificationSerializer,
    CompanyManagerEmailVerificationSerializer,
    CompanyManagerPhoneVerificationSerializer,
    CompanyUserRegistrationSerializer,
)
from .ncloud import get_api_keys
from dj_rest_auth.registration.views import RegisterView


class CompanyVerificationView(views.APIView):
    serializer_class = CompanyVerificationSerializer

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


class CompanyManagerPhoneSendView(views.APIView):
    def post(self, request):
        manager_phone = request.data.get("manager_phone")
        # 랜덤난수 생성
        manager_phone_auth_number = random.randint(100000, 999999)
        # 캐시 5분 저장
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
                "content": f"인증번호는 [{manager_phone_auth_number}]입니다. 인증번호를 정확히 입력해주세요.",
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


class CompanyManagerEmailSendView(views.APIView):
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


class CompanyUserRegisterView(RegisterView):
    serializer_class = CompanyUserRegistrationSerializer
