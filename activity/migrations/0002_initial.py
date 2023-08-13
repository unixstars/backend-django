# Generated by Django 4.2.3 on 2023-08-14 00:14

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):
    initial = True

    dependencies = [
        ("activity", "0001_initial"),
        ("user", "0001_initial"),
    ]

    operations = [
        migrations.AddField(
            model_name="suggestion",
            name="company_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="suggestion",
                to="user.companyuser",
            ),
        ),
        migrations.AddField(
            model_name="suggestion",
            name="student_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="suggestion",
                to="user.studentuser",
            ),
        ),
        migrations.AddField(
            model_name="scrap",
            name="board",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="scrap",
                to="activity.board",
            ),
        ),
        migrations.AddField(
            model_name="scrap",
            name="student_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="scrap",
                to="user.studentuser",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="activity",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="form",
                to="activity.activity",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="student_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="form",
                to="user.studentuser",
            ),
        ),
        migrations.AddField(
            model_name="form",
            name="student_user_portfolio",
            field=models.ForeignKey(
                default=None,
                null=True,
                on_delete=django.db.models.deletion.SET_NULL,
                related_name="form",
                to="user.studentuserportfolio",
            ),
        ),
        migrations.AddField(
            model_name="board",
            name="company_user",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="board",
                to="user.companyuser",
            ),
        ),
        migrations.AddField(
            model_name="activity",
            name="board",
            field=models.ForeignKey(
                on_delete=django.db.models.deletion.CASCADE,
                related_name="activity",
                to="activity.board",
            ),
        ),
    ]
