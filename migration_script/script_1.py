from django.db import migrations


# python manage.py makemigrations --empty program 후 아래 스크립트 복붙


def migrate_data_forward(apps, schema_editor):
    # AcceptedApplicant 외래키를 사용하여 Activity를 찾고 연결
    Assignment = apps.get_model("program", "Assignment")
    for assignment in Assignment.objects.all():
        assignment.activity = assignment.accepted_applicant.form.activity
        assignment.save()

    # AssignmentComment, Submit에 대해서도 같은 과정 반복
    AssignmentComment = apps.get_model("program", "AssignmentComment")
    for assignment_comment in AssignmentComment.objects.all():
        assignment_comment.accepted_applicant = (
            assignment_comment.assignment.accepted_applicant
        )
        assignment_comment.save()

    Submit = apps.get_model("program", "Submit")
    for submit in Submit.objects.all():
        submit.accepted_applicant = submit.assignment.accepted_applicant
        submit.save()


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
