from django.db import models


class AppConfiguration(models.Model):
    ENV_CHOICES = [
        ("dev", "Development"),
        ("prod", "Production"),
    ]

    minimum_app_version_name = models.CharField(max_length=50, default="0.0.0")
    minimum_app_version_code = models.IntegerField(default=0)
    maximum_app_version_name = models.CharField(max_length=50, default="0.0.0")
    maximum_app_version_code = models.IntegerField(default=0)
    ip_blacklist = models.JSONField(blank=True, null=True)
    environment = models.CharField(max_length=5, choices=ENV_CHOICES, default="dev")

    def save(self, *args, **kwargs):
        self.pk = 1
        super(AppConfiguration, self).save(*args, **kwargs)

    @classmethod
    def get_instance(cls):
        obj, created = cls.objects.get_or_create(pk=1)
        return obj

    def __str__(self) -> str:
        return "AppConfig"
