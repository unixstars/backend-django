from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Activity


@receiver(post_save, sender=Activity)
def limit_activities(sender, instance, **kwargs):
    if instance.board.activity.count() > 3:
        raise ValidationError("게시물은 최대 3개의 대외활동만 가질 수 있습니다.")
