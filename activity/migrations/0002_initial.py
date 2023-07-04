# Generated by Django 4.2 on 2023-06-15 07:50

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("user", "0001_initial"),
        ("activity", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="scrap",
            name="student_user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="user.studentuser"
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="activity_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="activity.activity"
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="student_user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="user.studentuser"
            ),
        ),
        migrations.AddField(
            model_name="board",
            name="company_user_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="user.companyuser"
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="board_id",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE, to="activity.board"
            ),
        ),
    ]
