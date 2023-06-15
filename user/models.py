from django.db import models
from django.contrib.auth.models import (
    AbstractBaseUser,
    BaseUserManager,
    PermissionsMixin,
)
from django.contrib.auth.validators import UnicodeUsernameValidator
from django.core.mail import send_mail
from activity.models import Form


class UserManager(BaseUserManager):
    def _create_user(self, username, email, password=None, **extra_fields):
        if not email:
            raise ValueError("이메일 주소를 입력해 주세요")
        email = self.normalize_email(email)
        username = self.model.normalize_username(username)
        user = self.model(username=username, email=email, **extra_fields)
        user.set_password(password)
        user.save(using=self.db)
        return user

    def create_user(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", False)
        extra_fields.setdefault("is_superuser", False)
        return self._create_user(username, email, password, **extra_fields)

    def create_superuser(self, username, email, password=None, **extra_fields):
        extra_fields.setdefault("is_staff", True)
        extra_fields.setdefault("is_superuser", True)

        if extra_fields.get("is_staff") is not True:
            raise ValueError("관리자 계정은 is_staff=True 여야 합니다.")
        if extra_fields.get("is_superuser") is not True:
            raise ValueError("관리자 계정은 is_superuser=True 여야 합니다.")

        return self._create_user(username, email, password, **extra_fields)


class User(AbstractBaseUser, PermissionsMixin):
    user_id = models.AutoField(primary_key=True)
    email = models.EmailField(unique=True)
    username = models.CharField(
        max_length=15, unique=False, validators=[UnicodeUsernameValidator()]
    )

    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)

    is_active = models.BooleanField(default=True)
    is_staff = models.BooleanField(default=False)

    USERNAME_FIELD = "email"
    EMAIL_FIELD = "email"
    REQUIRED_FIELDS = []

    objects = UserManager()

    def __str__(self):
        return self.username

    def clean(self):
        super().clean()
        self.email = self.__class__.objects.normalize_email(self.email)

    def email_user(self, subject, message, from_email=None, **kwargs):
        send_mail(subject, message, from_email, [self.email], **kwargs)

    class Meta:
        verbose_name = "기본유저모델"


class StudentUser(models.Model):
    student_user_id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)
    activity_id = models.ManyToManyField(
        "activity.Activity",
        through=Form,
    )

    class Meta:
        verbose_name = "학생유저"


class StudentUserProfile(models.Model):
    def get_upload_path(instance, filename):
        return "student/{}/profile_image/{}".format(
            instance.student_user_id.pk,
            filename,
        )

    student_user_profile_id = models.AutoField(primary_key=True)
    student_user_id = models.OneToOneField(StudentUser, on_delete=models.CASCADE)
    name = models.CharField(max_length=10)
    portfolio_image = models.ImageField(upload_to=get_upload_path)
    birth = models.DateField()
    phone_number = models.CharField(max_length=20)
    university = models.CharField(max_length=10)
    major = models.CharField(max_length=20)
    univ_email = models.EmailField(max_length=254)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class StudentUserPortfolio(models.Model):
    student_user_portfolio_id = models.AutoField(primary_key=True)
    student_user_id = models.ForeignKey(StudentUser, on_delete=models.CASCADE)
    title = models.CharField(max_length=20)
    contents = models.TextField(null=True, blank=True)
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PortfolioFiles(models.Model):
    portfolio_files_id = models.AutoField(primary_key=True)
    student_user_portfolio_id = models.OneToOneField(
        StudentUserPortfolio,
        on_delete=models.CASCADE,
    )
    created_at = models.DateTimeField(auto_now_add=True)
    updated_at = models.DateTimeField(auto_now=True)


class PortfolioOneFile(models.Model):
    def get_upload_path(instance, filename):
        return "student/{}/portfolio/{}/portfolio_files/{}".format(
            instance.portfolio_files_id.student_user_portfolio_id.student_user_id.pk,
            instance.portfolio_files_id.student_user_portfolio_id.pk,
            filename,
        )

    portfolio_one_file_id = models.AutoField(primary_key=True)
    portfolio_files_id = models.ForeignKey(
        PortfolioFiles,
        on_delete=models.CASCADE,
    )
    file = models.FileField(
        upload_to=get_upload_path,
        null=True,
        blank=True,
    )


class CompanyUser(models.Model):
    company_user_id = models.AutoField(primary_key=True)
    user_id = models.OneToOneField(User, on_delete=models.CASCADE)

    business_number = models.CharField(max_length=10)
    ceo_name = models.CharField(max_length=10)
    start_date = models.DateField()
    manager_phone = models.CharField(max_length=20)
    manager_email = models.EmailField()

    class Meta:
        verbose_name = "기업유저"
