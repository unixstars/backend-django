import boto3
from django.conf import settings
from botocore.exceptions import NoCredentialsError
import hashlib


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


def hash_function(data):
    m = hashlib.sha256()
    m.update(data.encode("utf-8"))
    result = m.hexdigest()
    return result
