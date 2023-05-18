import asyncio
import difflib
import requests
from pathlib import Path
from subprocess import CalledProcessError
from django.contrib import admin
from django.http import HttpResponseRedirect
from Antipirate_ver_2.core.models import Core
from Antipirate_ver_2.links.correlation import correlate
from Antipirate_ver_2.links.models import ParsedLink
from Antipirate_ver_2.links.parser import AsyncParser
from Antipirate_ver_2.links.services import LinksService
from Antipirate_ver_2.utils.converter import convert_to_mp3
from Antipirate_ver_2.utils.unwanted_domains import google_domains
from Antipirate_ver_2.whitelist.models import WhiteListDomain
from Antipirate_ver_2.links.send_report import send_report_selenium
from Antipirate_ver_2.reports.models import ReportedLinkModel, FakeLinkModel


@admin.action(description='Check links for music', )
def search_music(self, request, queryset):
    core = Core.objects.first()
    main_parser = AsyncParser()
    if not core.in_process:
        try:
            core.in_process = True
            core.save(update_fields=('in_process',))
            whitelist = google_domains + tuple(WhiteListDomain.objects.values_list(
                'domain', flat=True).distinct())
            links = list(queryset.values_list('link', flat=True).distinct())
            print(f'Total number of Google results to check: {len(links)}')
            music = asyncio.run(main_parser.main_process(links, deep=False))
            for obj in queryset:
                obj.checked = True
                if music.get(obj.link):
                    obj.music_found = True
                    obj.music_links = sorted(music.get(obj.link),
                                             key=lambda item: difflib.SequenceMatcher(None, item.lower(),
                                                                                      obj.music.title.lower()).ratio(),
                                             reverse=True)
            ParsedLink.objects.bulk_update(queryset, ['checked', 'music_found', 'music_links'])
        finally:
            core.in_process = False
            core.save(update_fields=('in_process',))
    else:
        print("Program is already running")


@admin.action(description='Analyze music', )
def compare_music(self, request, queryset):
    core = Core.objects.first()
    if not core.in_process:
        core.in_process = True
        core.save(update_fields=('in_process',))
        print("Starting process")

        for obj in queryset:
            if not obj.music_links:
                continue
            links = obj.music_links.strip("[]").strip("'").split("', '")
            for link in links:
                print(f'Checking link: {link}')

                # Download
                with requests.Session() as req:
                    try:
                        download = req.get(link)
                    except requests.exceptions.ConnectionError as e:
                        print(e)
                        continue

                if download.status_code != 200:
                    print(f'Response status code: {download.status_code}')
                    continue
                else:
                    file_name = link.split("/")[-1]
                    with open(f'uploads/target/{file_name}', 'wb') as f:
                        f.write(download.content)
                    my_file = Path(f'uploads/target/{file_name}')
                    if my_file.is_file():
                        print(f'Download complete: {file_name}')
                    if my_file.suffix != '.mp3':
                        my_file = convert_to_mp3(my_file)

                    # Correlate
                    try:
                        percent = correlate(source=f'{my_file}', target=str(obj.music.file.path))
                        if percent > 80:
                            print("MATCH FOUND")
                            obj.music_match = True
                            obj.music_links = link
                            obj.save(update_fields=('music_match', 'music_links'))
                            break
                        else:
                            print("No match")
                    except CalledProcessError as e:
                        print(f"Music file too short or corrupted. Error: {e}")

        # Removing downloaded music files
        LinksService.clear_folder(folder='uploads/target/')
        core.in_process = False
        core.save(update_fields=('in_process',))
        print("Process finished")


@admin.action(description='Send reports to Google', )
def send_reports(self, request, queryset):
    core = Core.objects.first()
    if not core.in_process:
        try:
            core.in_process = True
            core.save(update_fields=('in_process',))

            for obj in queryset:
                send_report_selenium(obj)
                ReportedLinkModel.objects.create(link=obj.link, domain=obj.domain, music=obj.music)
                obj.delete()

        finally:
            core.in_process = False
            core.save(update_fields=('in_process',))
    else:
        print("Program is already running")


@admin.action(description='Move fake links', )
def remove_fake_links(self, request, queryset):
    fakes = queryset.filter(fake_links=True)
    for obj in fakes:
        FakeLinkModel.objects.create(link=obj.link, music=obj.music, domain=obj.domain)
    fakes.delete()


@admin.register(ParsedLink)
class ParsedLinkAdmin(admin.ModelAdmin):
    list_display = (
        "domain",
        "link",
        "checked",
        "music_found",
        "music_match",
    )
    change_form_template = "core/change_view.html"

    def response_change(self, request, obj):
        if "_report" in request.POST:

            send_report_selenium(obj)
            ReportedLinkModel.objects.create(link=obj.link, domain=obj.domain, music=obj.music)
            obj.delete()

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    list_display_links = ("link",)
    actions = (search_music, compare_music, send_reports, remove_fake_links)
    readonly_fields = ('music', 'checked', 'music_found', 'music_links', "music_match")
    list_filter = ('music', 'checked', 'music_found', "music_match", "manual_check")
