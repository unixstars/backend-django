from django.db.models.signals import post_save
from django.dispatch import receiver
from django.core.exceptions import ValidationError
from .models import Activity, FormChatRoom
import logging

logger = logging.getLogger("client_errors")


@receiver(post_save, sender=Activity)
def limit_activities(sender, instance, **kwargs):
    if instance.board.activity.count() > 3:
        raise ValidationError("게시물은 최대 3개의 대외활동만 가질 수 있습니다.")


@receiver(post_save, sender=Activity)
def create_form_chatroom(sender, instance, created, **kwargs):
    if created:
        try:
            title = f"{instance.title} 지원자 채팅방"
            FormChatRoom.objects.create(activity=instance, title=title)
        except Exception as e:
            logger.error(f"ChatRoom 생성 실패: {e}")
