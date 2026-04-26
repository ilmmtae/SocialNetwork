from django.db import models
from django.conf import settings

class Group(models.Model):
    name = models.CharField(max_length=255)
    description = models.TextField(blank=True)
    members = models.ManyToManyField(settings.AUTH_USER_MODEL, related_name='user_groups')

    def __str__(self):
        return self.name