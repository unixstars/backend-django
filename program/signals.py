from django.db.models.signals import post_save
from django.dispatch import receiver
from .models import AcceptedApplicant, AcceptedChatRoom
from activity.models import Activity
import logging

logger = logging.getLogger("client_errors")


@receiver(post_save, sender=Activity)
def create_accepted_chatroom(sender, instance, created, **kwargs):
    if created:
        try:
            title = f"{instance.title} 합격자 채팅방"
            AcceptedChatRoom.objects.create(activity=instance, title=title)
        except Exception as e:
            logger.error(f"ChatRoom 생성 실패: {e}")
