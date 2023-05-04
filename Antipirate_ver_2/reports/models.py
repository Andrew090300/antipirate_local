from django.db import models
from Antipirate_ver_2.music.models import MusicModel
from Antipirate_ver_2.utils.models import TemporalModel
from Antipirate_ver_2.links.models import ParsedLink


class ReportedLinkModel(TemporalModel):

    link = models.URLField(max_length=1024, unique=True)
    domain = models.CharField(max_length=256, null=True, blank=True)
    music = models.ForeignKey(MusicModel, on_delete=models.CASCADE, blank=True, null=True)

    def __str__(self):
        return self.link
