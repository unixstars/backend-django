# Generated by Django 4.2.4 on 2023-09-17 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0004_alter_form_unique_together'),
    ]

    operations = [
        migrations.AddField(
            model_name='activity',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
        migrations.AddField(
            model_name='board',
            name='is_closed',
            field=models.BooleanField(default=False),
        ),
    ]
