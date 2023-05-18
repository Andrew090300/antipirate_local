import asyncio

from django.contrib import admin
from django.core.files.storage import FileSystemStorage
import pandas as pd


from Antipirate_ver_2.core.models import Core
from Antipirate_ver_2.links.parser import GoogleParser, AsyncParser
from Antipirate_ver_2.links.services import LinksService
from Antipirate_ver_2.music.models import MusicModel


@admin.action(description='Google parsing with automated analysis', )
def full_process_automated(self, request, queryset):
    if not Core.objects.exists():
        Core.objects.create()
    core = Core.objects.first()
    if not core.in_process:
        try:
            core.in_process = True
            core.save(update_fields=('in_process',))
            print("Starting to parse google")
            songs_list = queryset.values_list('title', flat=True).distinct()
            phrase = Core.objects.first().additional_phrase or ''
            for song in songs_list:
                query = f'{song} {phrase}' if phrase else f'{song}'
                song_model = MusicModel.objects.get(title=song)
                raw_links = set(GoogleParser.scrape_google(query=query))
                raw_audio = LinksService.search_music_auto(raw_links)
                result = LinksService.compare_music_auto(song_model, raw_audio)
                LinksService.links_to_db_auto(result, song=song_model)
            print("Finished")
        finally:
            core.in_process = False
            core.save(update_fields=('in_process',))
    else:
        print("Program is already running")


@admin.action(description='Parse google for links', )
def search_google(self, request, queryset):
    if not Core.objects.exists():
        Core.objects.create()
    core = Core.objects.first()
    if not core.in_process:
        try:
            core.in_process = True
            core.save(update_fields=('in_process',))
            print("Starting to parse google")
            #songs_list = queryset.values_list('title', flat=True).distinct()
            phrase = Core.objects.first().additional_phrase
            for song in queryset:
                main_parser = AsyncParser(song)
                #song_model = MusicModel.objects.get(title=song)
                query = f'{song.author} {song} {phrase}' if phrase else f'{song.author} {song}'
                print(query)
                unfiltered_links = GoogleParser.scrape_google(query=query)
                filtered_links = asyncio.run(main_parser.main_process(unfiltered_links, deep=True))
                LinksService.links_to_db(filtered_links, song=song)
            print("Finished")
        finally:
            core.in_process = False
            core.save(update_fields=('in_process',))
    else:
        print("Program is already running")


@admin.register(MusicModel)
class MusicModelAdmin(admin.ModelAdmin):
    list_display = (
        "title",
        "author",
        "created_at"
    )

    change_list_template = "music/music_admin.html"
    actions = (search_google,
               # full_process_automated,
               )

    def changelist_view(self, request, extra_context=None):

        if request.method == 'POST' and request.FILES.get('musicfile'):
            try:
                myfile = request.FILES['musicfile']
                fs = FileSystemStorage()
                fs.save(f'uploads/{myfile.name}', myfile)
                dbframe = pd.read_excel(io=f'uploads/{myfile.name}')
                for dbframe in dbframe.itertuples():
                    if not MusicModel.objects.filter(title=dbframe.title):
                        obj = MusicModel.objects.create(title=dbframe.title,)
                        obj.save()
                fs.delete(f'uploads/{myfile.name}')
            except Exception as e:
                print(e)
        response = super().changelist_view(
            request, extra_context, )
        return response

