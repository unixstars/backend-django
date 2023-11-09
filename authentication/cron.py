from django.utils import timezone
from rest_framework_simplejwt.token_blacklist.models import OutstandingToken
import logging

# 로거 설정
logger = logging.getLogger("cron_info")


def delete_expired_tokens():
    now = timezone.now()
    count, _ = OutstandingToken.objects.filter(expires_at__lt=now).delete()
    logger.info("Delete %d expired tokens at %s", count, now)
    logger.info("EXPIRED OUTSTANDING TOKEN DELETE COMPLETED %s", now)
