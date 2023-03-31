import os
from pathlib import Path
from django.core.files.storage import FileSystemStorage
from django.core.validators import FileExtensionValidator
from django.db import models

from Antipirate_ver_2.utils.converter import convert_to_mp3
from Antipirate_ver_2.utils.models import TemporalModel

fs = FileSystemStorage(location='uploads/source')


class MusicModel(TemporalModel):
    title = models.CharField(max_length=256, unique=True)
    link = models.URLField(max_length=1024, unique=True, null=True, verbose_name="sample url", blank=False)
    file = models.FileField(storage=fs, validators=[
        FileExtensionValidator(['mp3', 'aiff', 'wav'],
                               message="Invalid extension. Only mp3, wav or aiff is acceptable")])

    def __str__(self):
        return self.title

    def save(self, *args, **kwargs):
        new_file = self.file.path
        try:
            old_file = self.__class__.objects.get(id=self.id).file.path
            if new_file != old_file and os.path.exists(old_file):
                os.remove(old_file)
        except:
            pass

        super(MusicModel, self).save(*args, **kwargs)
        if Path(str(new_file)).suffix in ('.wav', '.aiff'):
            self.file = convert_to_mp3(self.file.path)
            super(MusicModel, self).save(*args, **kwargs)
