import time
from collections import deque
from rest_framework.throttling import BaseThrottle


class BurstRateThrottle(BaseThrottle):
    """
    매 duration초마다 rate수의 요청만 허가.
    """

    RATE = 1000  # 요청 수
    DURATION = 1  # 1초당

    def __init__(self):
        self.history = None

    def allow_request(self, request, view):
        now = time.time()
        if self.history is None:
            self.history = deque([now] * self.RATE, maxlen=self.RATE)
        elif (now - self.history[0]) < self.DURATION:
            # 히스토리의 첫 요청과 현재의 시간 차이가 duration보다 작은 경우.
            return self.throttle_failure()
        else:
            self.history.append(now)
            return self.throttle_success()

    def throttle_success(self):
        return True

    def throttle_failure(self):
        return False

    def wait(self):
        return None


import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError


# media 파일의 주소에 대해 사인된 url을 생성하는 함수
def generate_presigned_url(bucket_name, object_name, expiration=300):
    s3_client = boto3.client(
        "s3",
        aws_access_key_id=settings.AWS_ACCESS_KEY_ID,
        aws_secret_access_key=settings.AWS_SECRET_ACCESS_KEY,
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
import hashlib


def hash_function(data):
    return hashlib.sha256(data.encode()).hexdigest()
