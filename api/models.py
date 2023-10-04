from django.db import models


class AppConfiguration(models.Model):
    ENV_CHOICES = [
        ("dev", "Development"),
        ("prod", "Production"),
    ]

    minimum_app_version_name = models.CharField(max_length=50)
    minimum_app_version_code = models.IntegerField()
    maximum_app_version_name = models.CharField(max_length=50)
    maximum_app_version_code = models.IntegerField()
    ip_blacklist = models.JSONField(blank=True, null=True)
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
