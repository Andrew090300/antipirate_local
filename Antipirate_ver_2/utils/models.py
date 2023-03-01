from django.db import models


class TemporalModel(models.Model):
    created_at = models.DateTimeField(auto_now_add=True, blank=True, null=True)
    updated_at = models.DateTimeField(auto_now=True, blank=True, null=True)

    objects = models.Manager()

    class Meta:
        abstract = True
