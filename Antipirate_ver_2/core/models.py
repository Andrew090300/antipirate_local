from django.core.exceptions import ValidationError
from django.db import models

from Antipirate_ver_2.utils.models import TemporalModel


class Core(TemporalModel):

    class PeriodChoices(models.TextChoices):
        EVERY_HOUR = "Every hour"
        THREE_HOURS = "Every 3 hours"
        SIX_HOURS = "Every 6 hours"
        ONCE_A_DAY = "Once a day"
        ONCE_A_WEEK = "Once a week"

    title = models.CharField(max_length=128, default='Program Core')
    pages_number = models.IntegerField(null=True, blank=True)
    is_running = models.BooleanField(default=False)
   # parse_period = models.CharField(max_length=128, choices=PeriodChoices.choices, default=PeriodChoices.ONCE_A_DAY)
    additional_phrase = models.CharField(max_length=128, blank=True, null=True)
    in_process = models.BooleanField(default=False)

    def save(self, *args, **kwargs):
        if not self.pk and Core.objects.exists():
            raise ValidationError('There can be only one Core instance')
        return super(Core, self).save(*args, **kwargs)

    class Meta:
        verbose_name_plural = "Core"

    def __str__(self):
        return "Program Core"
