import os
import glob
from django.utils import timezone
import logging

logger = logging.getLogger("cron_info")


def clean_logs():
    now = timezone.now()
    logs_path = "/srv/backend-django/logs/*"
    files = glob.glob(logs_path)
    for f in files:
        try:
            if os.path.isfile(f) and os.stat(f).st_mtime < now - 7 * 86400:
                os.remove(f)
                print(f"Removed old log file: {f}")
        except Exception as e:
            print(f"Error removing file {f}: {e}")
