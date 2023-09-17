from django.db import models


class AppConfiguration(models.Model):
    ENV_CHOICES = [
        ("dev", "Development"),
        ("prod", "Production"),
    ]

    app_version_name = models.CharField(max_length=50)
    app_version_code = models.IntegerField()
    environment = models.CharField(max_length=5, choices=ENV_CHOICES)

    class Meta:
        abstract = True


class SingletonModel(AppConfiguration):
    class Meta:
        abstract = True

    def save(self, *args, **kwargs):
        self.pk = 1
        super(SingletonModel, self).save(*args, **kwargs)

    @classmethod
    def load(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj
