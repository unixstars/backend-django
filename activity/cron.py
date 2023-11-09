from django.utils import timezone
from .models import Board
import logging

# 로거 설정
logger = logging.getLogger("cron_info")


def close_expired_boards():
    now = timezone.now()
    boards = Board.objects.filter(is_closed=False)

    for board in boards:
        deadline = board.created_at + board.duration
        if now > deadline:
            board.is_closed = True
            logger.info("Close deadline expired board %s at %s", board, now)
            board.save()
        else:
            activities = board.activity.all()
            if all(activity.is_closed for activity in activities):
                board.is_closed = True
                logger.info("Close activity expired board %s at %s", board, now)
                board.save()
    logger.info("CLOSE BOARD CRON COMPLETED %s", now)
