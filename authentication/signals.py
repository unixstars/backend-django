from django.contrib.auth.signals import user_logged_in
from django.dispatch import receiver
from .models import LoginEvent
from api.utils import get_client_ip


@receiver(user_logged_in)
def log_user_logged_in(sender, user, request, **kwargs):
    ip_address = get_client_ip(request)
    event = LoginEvent(user=user, ip_address=ip_address)
    event.save()
