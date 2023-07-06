# Generated by Django 4.2 on 2023-07-06 09:44

from django.db import migrations, models
import django.db.models.deletion


class Migration(migrations.Migration):

    dependencies = [
        ('activity', '0002_initial'),
    ]

    operations = [
        migrations.AlterField(
            model_name='activity',
            name='board',
            field=models.ForeignKey(on_delete=django.db.models.deletion.CASCADE, related_name='activities', to='activity.board'),
        ),
        migrations.AlterField(
            model_name='activity',
            name='payment',
            field=models.CharField(default='없음', max_length=50),
        ),
    ]
