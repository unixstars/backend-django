# Generated by Django 4.2.3 on 2023-08-14 00:14

from django.db import migrations, models
import django.db.models.deletion
import program.models


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("activity", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="AcceptedApplicant",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("start_date", models.DateField(auto_now_add=True)),
                ("week", models.IntegerField(default=0)),
                (
                    "activity_status",
                    models.CharField(
                        choices=[
                            ("ongoing", "진행중"),
                            ("canceled", "취소"),
                            ("completed", "완료"),
                        ],
                        default="ongoing",
                        max_length=10,
                    ),
                ),
                (
                    "form",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="accepted_applicant",
                        to="activity.form",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Assignment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=30)),
                ("content", models.TextField()),
                (
                    "progress_status",
                    models.CharField(
                        choices=[
                            ("in_progress", "진행중"),
                            ("first_revision", "1차수정"),
                            ("second_revision", "2차수정"),
                            ("final_approval", "최종승인"),
                        ],
                        default="in_progress",
                        max_length=30,
                    ),
                ),
                ("duration", models.DurationField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "accepted_applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignment",
                        to="program.acceptedapplicant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notice",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("title", models.CharField(max_length=30)),
                ("content", models.TextField()),
                ("is_checked", models.BooleanField(default=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "accepted_applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notice",
                        to="program.acceptedapplicant",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Submit",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField(blank=True, null=True)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assignment",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submit",
                        to="program.assignment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubmitFile",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                (
                    "file",
                    models.FileField(
                        upload_to=program.models.SubmitFile.get_upload_path_file
                    ),
                ),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "submit",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="submit_file",
                        to="program.submit",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="NoticeComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user_type",
                    models.CharField(
                        choices=[("student", "학생유저"), ("company", "기업유저")],
                        default="student",
                        max_length=10,
                    ),
                ),
                (
                    "notice",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="notice_comment",
                        to="program.notice",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="AssignmentComment",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "user_type",
                    models.CharField(
                        choices=[("student", "학생유저"), ("company", "기업유저")],
                        default="student",
                        max_length=10,
                    ),
                ),
                (
                    "assignment",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="assignment_comment",
                        to="program.assignment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="ApplicantWarning",
            fields=[
                (
                    "id",
                    models.BigAutoField(
                        auto_created=True,
                        primary_key=True,
                        serialize=False,
                        verbose_name="ID",
                    ),
                ),
                ("content", models.CharField(max_length=50)),
                (
                    "accepted_applicant",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        related_name="applicant_warning",
                        to="program.acceptedapplicant",
                    ),
                ),
            ],
        ),
    ]
