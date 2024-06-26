import os, requests, random, string
from rest_framework import generics, parsers, views, status
from rest_framework.response import Response
from rest_framework.permissions import IsAuthenticated
from rest_framework.exceptions import NotFound
from django.contrib.auth import authenticate
from django.core.cache import cache
from django.utils import timezone
from authentication.utils import SendRateThrottle
from authentication.ncloud import get_api_keys
from api.permissions import (
    IsStudentUser,
    IsCompanyUser,
    IsPortFolioOwner,
    IsProfileOwner,
)
from api.utils import hash_function
from .models import StudentUserPortfolio, StudentUserProfile, CompanyUser
from .serializers import (
    StudentUserPortfolioSerializer,
    StudentUserPortfolioUpdateSerializer,
    StudentUserPortfolioListSerializer,
    StudentUserProfileSerializer,
    StudentUserProfileUpdateSerializer,
    CompanyUserInfoSerializer,
    CompanyUserInfoChangePhoneVerificationSerializer,
    CompanyUserInfoChangeSerializer,
)


# 포트폴리오 추가: 학생 유저 포트폴리오 생성
class StudentUserPortFolioCreateView(generics.CreateAPIView):
    queryset = StudentUserPortfolio.objects.all()
    serializer_class = StudentUserPortfolioSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)


# 포트폴리오/포트폴리오1 : 학생 유저 포트폴리오 하나 보기,수정,삭제
class StudentUserPortfolioDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = StudentUserPortfolio.objects.all()
    serializer_class = StudentUserPortfolioUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsPortFolioOwner,
    ]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]


# 포트폴리오 : 학생 유저 포트폴리오 리스트
class StudentUserPortfolioListView(generics.ListAPIView):
    serializer_class = StudentUserPortfolioListSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsPortFolioOwner,
    ]

    def get_queryset(self):
        user = self.request.user.student_user
        return StudentUserPortfolio.objects.filter(student_user=user)


# 프로필/수정페이지 : 학생 유저 프로필 생성
class StudentUserProfileCreateView(generics.CreateAPIView):
    queryset = StudentUserProfile.objects.all()
    serializer_class = StudentUserProfileSerializer
    permission_classes = [IsAuthenticated, IsStudentUser]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def perform_create(self, serializer):
        serializer.save(student_user=self.request.user.student_user)


# 프로필 : 학생 유저 프로필 하나 보기,수정,삭제
class StudentUserProfileDetailView(generics.RetrieveUpdateDestroyAPIView):
    serializer_class = StudentUserProfileUpdateSerializer
    permission_classes = [
        IsAuthenticated,
        IsStudentUser,
        IsProfileOwner,
    ]
    parser_classes = [
        parsers.MultiPartParser,
        parsers.FormParser,
        parsers.JSONParser,
    ]

    def get_object(self):
        try:
            student_user = self.request.user.student_user
            profile = StudentUserProfile.objects.get(student_user=student_user)
            return profile
        except StudentUserProfile.DoesNotExist:
            raise NotFound(detail="학생 프로필이 존재하지 않습니다.")


class CheckStudentUserProfileView(views.APIView):
    permission_classes = [IsAuthenticated, IsStudentUser]

    def get(self, request, *args, **kwargs):
        student_user = request.user.student_user
        profile_exists = StudentUserProfile.objects.filter(
            student_user=student_user
        ).exists()
        return Response({"exists": profile_exists}, status=status.HTTP_200_OK)


# 프로필/수정페이지/계좌인증
class StudentBankAccountCheckView(views.APIView):
    permission_classes = [IsAuthenticated, IsStudentUser]

    BANK_CODE_MAP = {
        "한국은행": "001",
        "산업은행": "002",
        "기업은행": "003",
        "국민은행": "004",
        "NH농협은행": "011",
        "우리은행": "020",
        "새마을금고": "045",
        "하나은행": "081",
        "신한은행": "088",
        "카카오뱅크": "090",
        "토스뱅크": "092",
    }

    def post(self, request):
        bank_name = request.data.get("bank")
        account_num = request.data.get("account_number")
        account_holder_info = request.data.get("social_number")
        account_holder_name = request.data.get("name")

        if not all([bank_name, account_num, account_holder_info, account_holder_name]):
            return Response(
                {"error": "필수 파라미터가 누락되었습니다."},
                status=status.HTTP_400_BAD_REQUEST,
            )

        bank_code_std = self.BANK_CODE_MAP.get(bank_name)
        if not bank_code_std:
            return Response(
                {"error": "Invalid bank name"}, status=status.HTTP_400_BAD_REQUEST
            )

        tran_dtime = timezone.now().strftime("%Y%m%d%H%M%S")
        bank_tran_id = (
            os.getenv("UNIQUE_CODE")
            + "U"
            + "".join(random.choices(string.ascii_uppercase + string.digits, k=9))
        )

        payload = {
            "bank_tran_id": bank_tran_id,
            "bank_code_std": bank_code_std,
            "account_num": account_num,
            "account_holder_info_type": " ",
            "account_holder_info": account_holder_info,
            "tran_dtime": tran_dtime,
        }

        headers = {
            "Content-Type": "application/json; charset=UTF-8",
            "Authorization": f"Bearer {os.getenv('ACCESS_TOKEN')}",
        }

        response = requests.post(
            "https://openapi.openbanking.or.kr/v2.0/inquiry/real_name",
            json=payload,
            headers=headers,
        )
        if response.status_code == 200:
            resp_data = response.json()
            if resp_data.get(
                "account_holder_name"
            ) == account_holder_name and resp_data.get("account_type") in {
                "1",
                "2",
                "6",
            }:
                return Response({"detail": "인증이 완료되었습니다."}, status=status.HTTP_200_OK)
            else:
                return Response(
                    {"detail": "인증이 실패하였습니다."}, status=status.HTTP_400_BAD_REQUEST
                )
        else:
            return Response(
                {"detail": "인증 서버에서 오류가 발생했습니다."},
                status=status.HTTP_500_INTERNAL_SERVER_ERROR,
            )


# 내 정보/기업회원
class CompanyUserInfoView(generics.RetrieveAPIView):
    serializer_class = CompanyUserInfoSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def get_object(self):
        user = self.request.user
        return CompanyUser.objects.get(user=user)


# 회원정보 변경 인증
class CompanyUserInfoAuthView(views.APIView):
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def post(self, request, *args, **kwargs):
        user = authenticate(
            email=request.user.email, password=request.data.get("password")
        )
        if user is not None:
            cache.set(
                hash_function(request.user.email) + "_authenticated", True, 10 * 60
            )
            return Response({"detail": "비밀번호가 유효합니다."}, status=status.HTTP_200_OK)
        return Response(
            {"detail": "비밀번호가 유효하지 않습니다."}, status=status.HTTP_400_BAD_REQUEST
        )


# 회원정보 /비밀번호 변경:담당자 연락처 인증번호 전송
class CompanyUserInfoChangePhoneSendView(views.APIView):
    permission_classes = [IsAuthenticated, IsCompanyUser]
    throttle_classes = [SendRateThrottle]
    throttle_field = "new_manager_phone"

    def post(self, request):
        auth_info = cache.get(hash_function(request.user.email) + "_authenticated")
        if not auth_info:
            return Response({"detail": "비밀번호 인증이 되지 않았습니다."}, status=400)

        new_manager_phone = request.data.get("new_manager_phone")
        new_manager_phone_auth_number = random.randint(100000, 999999)
        cache.set(
            hash_function(new_manager_phone), new_manager_phone_auth_number, 60 * 5
        )

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
                "subject": "[유니스타 기업정보변경 담당자 번호인증]",
                "content": f"유니스타 기업정보변경 인증번호는 [{new_manager_phone_auth_number}]입니다. 인증번호를 정확히 입력해주세요.",
                "messages": [{"to": f"{new_manager_phone}"}],
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


# 회원정보 /비밀번호 변경:담당자 연락처 인증번호 인증
class CompanyUserInfoChangePhoneVerificationView(views.APIView):
    serializer_class = CompanyUserInfoChangePhoneVerificationSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def post(self, request):
        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        new_manager_phone = serializer.validated_data.get("new_manager_phone")
        auth_number = serializer.validated_data.get("auth_number")

        correct_auth_number = cache.get(hash_function(new_manager_phone))

        if correct_auth_number is None:
            return Response({"detail": "인증번호가 만료되었습니다."}, status=400)
        elif correct_auth_number != auth_number:
            return Response({"detail": "잘못된 인증번호 입니다."}, status=400)
        else:
            # 인증여부 캐시에 추가(정보변경에 활용)
            cache.set(
                hash_function(new_manager_phone) + "_authenticated", True, 60 * 60
            )
            return Response({"detail": "인증에 성공하였습니다."})


# 회원정보/비밀번호 변경: 회원정보/비밀번호 변경 버튼
class CompanyUserInfoChangeView(views.APIView):
    serializer_class = CompanyUserInfoChangeSerializer
    permission_classes = [IsAuthenticated, IsCompanyUser]

    def post(self, request, *args, **kwargs):
        auth_info = cache.get(hash_function(request.user.email) + "_authenticated")
        if not auth_info:
            return Response({"detail": "비밀번호 인증이 되지 않았습니다."}, status=400)

        serializer = self.serializer_class(data=request.data)
        serializer.is_valid(raise_exception=True)

        user = request.user
        new_password = serializer.validated_data.get("new_password1")
        new_manager_phone = serializer.validated_data.get("new_manager_phone")

        if new_manager_phone:
            authenticated = cache.get(
                hash_function(new_manager_phone) + "_authenticated"
            )
            if not authenticated:
                return Response(
                    {"detail": "담당자 전화번호 인증이 필요합니다."},
                    status=status.HTTP_400_BAD_REQUEST,
                )

        if new_password:
            user.set_password(new_password)
            user.save()

        if new_manager_phone:
            try:
                company_user = user.company_user
                company_user.manager_phone = new_manager_phone
                company_user.save()
            except CompanyUser.DoesNotExist:
                return Response(
                    {"detail": "기업 유저 정보가 없습니다."}, status=status.HTTP_400_BAD_REQUEST
                )

        return Response({"detail": "정보가 성공적으로 변경되었습니다."}, status=status.HTTP_200_OK)
