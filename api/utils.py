import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError
import hashlib
from rest_framework.throttling import SimpleRateThrottle


# media 파일의 주소에 대해 사인된 url을 생성하는 함수
def generate_presigned_url(bucket_name, object_name, expiration=300):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
        region_name=settings.AWS_REGION,
    )
    try:
        response = s3_client.generate_presigned_url(
            "get_object",
            Params={"Bucket": bucket_name, "Key": object_name},
            ExpiresIn=expiration,
        )
    except NoCredentialsError:
        return None

    return response


# hash 함수, one way
def hash_function(data):
    m = hashlib.sha256()
    m.update(data.encode("utf-8"))
    result = m.hexdigest()
    return result


# request의 특정항목에 대한 제한
class FieldRateThrottle(SimpleRateThrottle):
    rate = None
    field = None

    def get_cache_key(self, request, view):
        self.field = getattr(view, "throttle_field", None)
        if self.field and self.field in request.data:
            return self.cache_format % {
                "scope": self.scope,
                "ident": request.data[self.field],
            }

        return None


# 유저의 ip 주소 얻기
def get_client_ip(request):
    x_forwarded_for = request.META.get("HTTP_X_FORWARDED_FOR")
    if x_forwarded_for:
        ip = x_forwarded_for.split(",")[0]
    else:
        ip = request.META.get("REMOTE_ADDR")
    return ip
