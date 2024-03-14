from django.db import migrations


# python manage.py makemigrations --empty program 후 아래 스크립트 복붙


def migrate_data_forward(apps, schema_editor):
    Notice = apps.get_model("program", "Notice")
    for notice in Notice.objects.all():
        notice.activity = notice.accepted_applicant.form.activity
        notice.save()

    NoticeComment = apps.get_model("program", "NoticeComment")
    for notice_comment in NoticeComment.objects.all():
        notice_comment.accepted_applicant = notice_comment.assignment.accepted_applicant
        notice_comment.save()


def migrate_data_backward(apps, schema_editor):
    # 롤백 시 특별히 수행할 작업이 없는 경우 pass
    pass


class Migration(migrations.Migration):

    # dev,prod에 따라 다른 마이그레이션 파일 이름 적용
    dependencies = [
        ("program", "0007_assignment_activity_and_more"),
    ]

    operations = [
        migrations.RunPython(migrate_data_forward, migrate_data_backward),
    ]
