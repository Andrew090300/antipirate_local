from django.db import models
from Antipirate_ver_2.links.models import ParsedLink
from Antipirate_ver_2.utils.models import TemporalModel


class WhiteListDomain(TemporalModel):

    title = models.CharField(max_length=256, unique=True)
    domain = models.CharField(max_length=256)

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        ParsedLink.objects.filter(link__startswith=self.domain).delete()
        super(WhiteListDomain, self).save(*args, **kwargs)

