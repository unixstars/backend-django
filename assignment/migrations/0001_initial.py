# Generated by Django 4.2 on 2023-06-15 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("activity", "0001_initial"),
    ]

    operations = [
        migrations.CreateModel(
            name="Assignment",
            fields=[
                ("assignment_id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                (
                    "form_id",
                    models.OneToOneField(
                        on_delete=django.db.models.deletion.CASCADE, to="activity.form"
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="Notice",
            fields=[
                ("notice_id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=30)),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "assignment_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="assignment.assignment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubmitFiles",
            fields=[
                ("submitfiles_id", models.AutoField(primary_key=True, serialize=False)),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
            ],
        ),
        migrations.CreateModel(
            name="WeekAssign",
            fields=[
                ("week_assign_id", models.AutoField(primary_key=True, serialize=False)),
                ("title", models.CharField(max_length=30)),
                ("content", models.TextField()),
                ("week", models.IntegerField()),
                ("is_approve", models.BooleanField(default=False)),
                (
                    "assignment_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="assignment.assignment",
                    ),
                ),
            ],
        ),
        migrations.CreateModel(
            name="SubmitOneFile",
            fields=[
                ("file_id", models.AutoField(primary_key=True, serialize=False)),
                ("file", models.FileField(upload_to="")),
                (
                    "submitfiles_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="assignment.submitfiles",
                    ),
                ),
            ],
        ),
        migrations.AddField(
            model_name="submitfiles",
            name="week_assign_id",
            field=models.OneToOneField(
                on_delete=django.db.models.deletion.CASCADE, to="assignment.weekassign"
            ),
        ),
        migrations.CreateModel(
            name="NoticeComment",
            fields=[
                (
                    "notice_comment_id",
                    models.AutoField(primary_key=True, serialize=False),
                ),
                ("content", models.TextField()),
                ("created_at", models.DateTimeField(auto_now_add=True)),
                ("updated_at", models.DateTimeField(auto_now=True)),
                (
                    "notice_id",
                    models.ForeignKey(
                        on_delete=django.db.models.deletion.CASCADE,
                        to="assignment.notice",
                    ),
                ),
            ],
        ),
    ]