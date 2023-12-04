from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.core.mail import send_mail


class UserManager(BaseUserManager):
    def _create_user(self, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일 주소를 입력해 주세요")
        email = self.normalize_email(email)
        user = self.model(email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(email, password, **extra_fields)

    def create_superuser(self, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("관리자 계정은 is_staff=True 여야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("관리자 계정은 is_superuser=True 여야 합니다.")

        return self._create_user(email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    username = None
    email = models.EmailField(unique=True)

    is_company_user = models.BooleanField(default=False)

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.email

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        verbose_name = "User"


class CompanyUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="company_user"
    )

    business_number = models.CharField(max_length=10, unique=True)
    ceo_name = models.CharField(max_length=10)
    start_date = models.DateField()
    corporate_number = models.CharField(max_length=13, unique=True)
    manager_phone = models.CharField(max_length=20, unique=True)
    manager_email = models.EmailField(unique=True)

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "CompanyUser"


class StudentUser(models.Model):
    user = models.OneToOneField(
        User, on_delete=models.CASCADE, primary_key=True, related_name="student_user"
    )

    def __str__(self):
        return self.user.email

    class Meta:
        verbose_name = "StudentUser"


class StudentUserProfile(models.Model):
    def get_upload_path_profile_image(instance, filename):
        return "student/{}/profile_image/{}".format(
            instance.student_user.pk,
            filename,
        )

    def get_upload_path_certificate(instance, filename):
        return "student/{}/univ_certificate/{}".format(
            instance.student_user.pk,
            filename,
        )

    student_user = models.OneToOneField(
        StudentUser, on_delete=models.CASCADE, related_name="student_user_profile"
    )

    name = models.CharField(max_length=10)
    profile_image = models.ImageField(
        upload_to=get_upload_path_profile_image, null=True, default=None
    )
    birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    university = models.CharField(max_length=20)
    major = models.CharField(max_length=30)
    univ_certificate = models.FileField(upload_to=get_upload_path_certificate)
    bank = models.CharField(max_length=20)
    account_number = models.CharField(max_length=100)
    social_number = models.CharField(max_length=13, default="")
    address = models.TextField(default="")
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.student_user}/{self.name}의 프로필"


class StudentUserPortfolio(models.Model):
    student_user = models.ForeignKey(
        StudentUser,
        on_delete=models.SET_NULL,
        null=True,
        related_name="student_user_portfolio",
    )

    title = models.CharField(max_length=20)
    content = models.TextField(null=True, blank=True)
    description = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    def __str__(self) -> str:
        return f"{self.student_user}의 {self.title}"


class PortfolioFile(models.Model):
    def get_upload_path(instance, filename):
        return "student/{}/portfolio/{}/portfolio_files/{}".format(
            instance.student_user_portfolio.student_user.pk,
            instance.student_user_portfolio.pk,
            filename,
        )

    student_user_portfolio = models.ForeignKey(
        StudentUserPortfolio, on_delete=models.CASCADE, related_name="portfolio_file"
    )

    file = models.FileField(upload_to=get_upload_path)

    def __str__(self) -> str:
        return f"{self.student_user_portfolio}의 {self.file}"
