from django.db import models
from user.models import CompanyUser, StudentUser, StudentUserPortfolio


class Board(models.Model):
    def get_upload_path_logo(instance, filename):
        return "company/{}/logo/{}".format(
            instance.company_user.pk,
            filename,
        )

    def get_upload_path_banner(instance, filename):
        return "company/{}/banner/{}".format(
            instance.company_user.pk,
            filename,
        )

    company_user = models.ForeignKey(
        CompanyUser, on_delete=models.CASCADE, related_name="board"
    )

    logo = models.ImageField(
        upload_to=get_upload_path_logo,
        null=True,
        blank=True,
        max_length=200,
    )
    banner = models.ImageField(
        upload_to=get_upload_path_banner,
        null=True,
        blank=True,
        max_length=200,
    )
    title = models.CharField(
        max_length=30,
        null=True,
        blank=True,
    )
    company_name = models.CharField(max_length=30)
    introduction = models.TextField()
    vision = models.TextField()
    pride = models.CharField(
        max_length=300,
        null=True,
        blank=True,
    )
    address = models.CharField(max_length=150)
    duration = models.DurationField()
    views = models.PositiveIntegerField(default=0)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
    duration_extended = models.IntegerField(default=0)
    is_closed = models.BooleanField(default=False)
    is_admitted = models.BooleanField(default=False)

    def __str__(self):
        company = self.company_name
        title = self.title
        return f"{company}의 {title}"


class Activity(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="activity")

    title = models.CharField(max_length=20)
    kind = models.CharField(max_length=20)
    people_number = models.IntegerField()
    talent = models.TextField()
    frequency = models.TextField(default="")
    way = models.TextField()
    period = models.DurationField()
    recruit = models.BooleanField(default=False)
    payment = models.CharField(
        max_length=50,
        default="없음",
    )
    is_closed = models.BooleanField(default=False)

    def __str__(self):
        return self.title


class Scrap(models.Model):
    board = models.ForeignKey(Board, on_delete=models.CASCADE, related_name="scrap")
    student_user = models.ForeignKey(
        StudentUser, on_delete=models.CASCADE, related_name="scrap"
    )

    class Meta:
        unique_together = [
            "board",
            "student_user",
        ]

    def __str__(self) -> str:
        return f"{self.student_user}의 {self.board} 스크랩"


class Form(models.Model):
    student_user = models.ForeignKey(
        StudentUser, on_delete=models.CASCADE, related_name="form"
    )
    activity = models.ForeignKey(
        Activity, on_delete=models.CASCADE, related_name="form"
    )
    student_user_portfolio = models.ForeignKey(
        StudentUserPortfolio,
        on_delete=models.SET_NULL,
        related_name="form",
        null=True,
        blank=True,
        default=None,
    )

    PENDING, WAITING, CANCELED, REJECTED, ACCEPTED = (
        "pending",
        "waiting",
        "canceled",
        "rejected",
        "accepted",
    )

    ACCEPT_STATUS_CHOICES = [
        (PENDING, "대기중"),
        (WAITING, "확정대기"),
        (CANCELED, "활동취소"),
        (REJECTED, "불합격"),
        (ACCEPTED, "합격"),
    ]

    introduce = models.TextField(default="")
    reason = models.TextField(default="")
    merit = models.TextField(default="")
    accept_status = models.CharField(
        max_length=10,
        choices=ACCEPT_STATUS_CHOICES,
        default=PENDING,
    )
    submitted_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        unique_together = [
            "student_user",
            "activity",
        ]

    def __str__(self) -> str:
        return f"{self.student_user.student_user_profile.name}의 {self.activity.board}/{self.activity} 지원서"


class Suggestion(models.Model):
    company_user = models.ForeignKey(
        CompanyUser, on_delete=models.CASCADE, related_name="suggestion"
    )
    student_user = models.ForeignKey(
        StudentUser, on_delete=models.CASCADE, related_name="suggestion"
    )
    created_at = models.DateTimeField(auto_now_add=True)

    def __str__(self) -> str:
        return f"{self.company_user}의 {self.student_user} 지원제안"


class Communication(models.Model):

    activity = models.OneToOneField(
        Activity, on_delete=models.CASCADE, related_name="communication"
    )

    STUDENT, COMPANY = "student", "company"
    USER_TYPE_CHOICES = (
        (STUDENT, "학생유저"),
        (COMPANY, "기업유저"),
    )
    content = models.TextField()
    user_type = models.CharField(
        max_length=10, choices=USER_TYPE_CHOICES, default=COMPANY
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class CommunicationComment(models.Model):

    communication = models.ForeignKey(
        Communication, on_delete=models.CASCADE, related_name="communication_comment"
    )
    form = models.ForeignKey(
        Form,
        on_delete=models.SET_NULL,
        null=True,
        blank=True,
        related_name="communication_comment",
    )

    title = models.CharField(max_length=30)
    content = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)
