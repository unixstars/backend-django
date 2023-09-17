from datetime import timedelta
from django.utils import timezone
from .models import AcceptedApplicant


def update_accepted_applicants():
    now = timezone.now()
    for applicant in AcceptedApplicant.objects.filter(
        activity_status=AcceptedApplicant.ONGOING
    ):
        activity_duration_in_weeks = applicant.form.activity.period.total_seconds() // (
            60 * 60 * 24 * 7
        )
        if applicant.form.activity.period.total_seconds() % (60 * 60 * 24 * 7) > 0:
            activity_duration_in_weeks += 1

        days_passed = (now - applicant.start_date).days
        weeks_passed = days_passed // 7

        if weeks_passed > activity_duration_in_weeks:
            applicant.activity_status = AcceptedApplicant.COMPLETED
        else:
            applicant.week += weeks_passed
            applicant.start_date += timedelta(days=weeks_passed * 7)

        applicant.save()
