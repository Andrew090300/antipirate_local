from django.db import models

from Antipirate_ver_2.music.models import MusicModel
from Antipirate_ver_2.utils.models import TemporalModel


class ParsedLink(TemporalModel):

    link = models.URLField(max_length=1024, unique=True)
    domain = models.CharField(max_length=256, null=True, blank=True)
    blocked = models.BooleanField(default=False)
    reports_num = models.IntegerField(default=0)
    music = models.ForeignKey(MusicModel, on_delete=models.CASCADE, blank=True, null=True)
    checked = models.BooleanField(default=False)
    music_found = models.BooleanField(default=False)
    music_links = models.TextField(blank=True, null=True)
    manual_check = models.BooleanField(default=False)
    music_match = models.BooleanField(default=False)

    def __str__(self):
        return self.link
