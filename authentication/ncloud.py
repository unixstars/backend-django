import os, hashlib, hmac, base64, time


def get_api_keys(uri, method):
    timestamp = str(int(time.time() * 1000))
    access_key = os.getenv("NCLOUD_ACCESS_KEY")
    secret_key = bytes(os.getenv("NCLOUD_SECRET_KEY"), "UTF-8")
    message = method + " " + uri + "\n" + timestamp + "\n" + access_key
    message = bytes(message, "UTF-8")
    signing_key = base64.b64encode(
        hmac.new(secret_key, message, digestmod=hashlib.sha256).digest()
    )
    return timestamp, access_key, signing_key
