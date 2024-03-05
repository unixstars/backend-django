from django.utils.deprecation import MiddlewareMixin
import logging

logger = logging.getLogger("api.middleware")

# 요청 카운터를 저장할 딕셔너리
request_counts = {}


class LogHeaderMiddleware(MiddlewareMixin):
    def process_request(self, request):
        # 클라이언트 IP 주소 가져오기. X-Forwarded-For 헤더를 사용하는 경우 고려
        ip = request.META.get("HTTP_X_FORWARDED_FOR") or request.META.get("REMOTE_ADDR")

        # 해당 IP 주소의 요청 수 카운트
        count = request_counts.get(ip, 0) + 1
        request_counts[ip] = count

        # 10,000번 이상의 요청이 있는 경우, 요청 헤더 로깅
        if count >= 10000:
            headers = {k: v for k, v in request.headers.items()}
            logger.info(
                f"IP {ip} has made {count} requests. Request Headers: {headers}"
            )
