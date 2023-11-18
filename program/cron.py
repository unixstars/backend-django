from datetime import timedelta
from django.utils import timezone
from .models import AcceptedApplicant
import logging

logger = logging.getLogger("cron_info")


def update_accepted_applicants():
    now = timezone.now()
    logger.info("Update accepted applicants cron job started at %s", now)
    for applicant in AcceptedApplicant.objects.filter(
        activity_status=AcceptedApplicant.ONGOING
    ):
        activity_duration_in_weeks = applicant.form.activity.period.total_seconds() // (
            60 * 60 * 24 * 7
        )
        if applicant.form.activity.period.total_seconds() % (60 * 60 * 24 * 7) > 0:
            activity_duration_in_weeks += 1

        days_passed = (now.date() - applicant.start_date).days
        weeks_passed = days_passed // 7

        if weeks_passed > applicant.week:
            applicant.week = weeks_passed
        logger.info("Update applicant week %s at %s", applicant, now)
        if weeks_passed >= activity_duration_in_weeks:
            applicant.activity_status = AcceptedApplicant.COMPLETED
        logger.info("Update applicant COMPLETE %s at %s", applicant, now)
        applicant.save()

    logger.info("CLOSE UPDATE APPLICANT WEEK %s", now)
