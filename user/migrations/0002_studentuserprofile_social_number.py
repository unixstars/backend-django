# Generated by Django 4.2.4 on 2023-09-17 19:29

from django.db import migrations, models


class Migration(migrations.Migration):

    dependencies = [
        ('user', '0001_initial'),
    ]

    operations = [
        migrations.AddField(
            model_name='studentuserprofile',
            name='social_number',
            field=models.CharField(default='', max_length=13),
        ),
    ]
