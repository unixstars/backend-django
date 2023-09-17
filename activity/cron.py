from django.utils import timezone
from .models import Board


def close_expired_boards():
    now = timezone.now()
    boards = Board.objects.filter(is_closed=False)

    for board in boards:
        deadline = board.created_at + board.duration
        if now > deadline:
            board.is_closed = True
            board.save()
        else:
            activities = board.activity.all()
            if all(activity.is_closed for activity in activities):
                board.is_closed = True
                board.save()
