import asyncio
import os
import shutil
from pathlib import Path
from subprocess import CalledProcessError
from urllib.parse import urlparse

import requests
from Antipirate_ver_2.links.correlation import correlate
from Antipirate_ver_2.links.models import ParsedLink
from Antipirate_ver_2.links.parser import AsyncParser
from Antipirate_ver_2.utils.converter import convert_to_mp3
from Antipirate_ver_2.utils.unwanted_domains import google_domains
from Antipirate_ver_2.whitelist.models import WhiteListDomain


class LinksService:

    @staticmethod
    def links_to_db_auto(links_array, song):
        ParsedLink.objects.bulk_create(
            [ParsedLink(link=link, music=song, domain=urlparse(link).netloc, music_links=match, music_found=True,
                        music_match=True, checked=True) for link, match in
             links_array.items()],
            ignore_conflicts=True,
        )

    @staticmethod
    def links_to_db(links_array, song):
        ParsedLink.objects.bulk_create(
            [ParsedLink(link=link, music=song, domain=urlparse(link).netloc, manual_check=True) for link in
             set(links_array)],
            ignore_conflicts=True,
        )

    @staticmethod
    def clear_folder(folder):
        for filename in os.listdir(folder):
            file_path = os.path.join(folder, filename)
            try:
                if os.path.isfile(file_path) or os.path.islink(file_path):
                    os.unlink(file_path)
                elif os.path.isdir(file_path):
                    shutil.rmtree(file_path)
            except Exception as e:
                print(f'Failed to delete {file_path}. Reason: {e}')

    @staticmethod
    def search_music_auto(array: set):
        main_parser = AsyncParser()
        if main_parser:
            links = list(array)
            print(f'Total number of Google results to check: {len(links)}')
            music = asyncio.run(main_parser.main_process(links, deep=False))
            return music

    @staticmethod
    def compare_music_auto(obj, music: dict):
        count = 0
        matches_count = 0
        initial = {x: len(y) for x, y in music.items()}
        print(initial)
        result_music = dict()
        for x, y in music.items():
            for ind, link in enumerate(y):
                print(f'Checking link: {link}')
                count += 1
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
                        percent = correlate(source=f'{my_file}', target=str(obj.file.path))
                        if percent > 80:
                            print("MATCH FOUND")
                            result_music[x] = link
                            matches_count += 1
                        # break
                        else:
                            print("No match")
                    except CalledProcessError as e:
                        print(f"Music file too short or corrupted. Error: {e}")

        print(count)
        print(matches_count)
        # Removing downloaded music files
        LinksService.clear_folder(folder='uploads/target/')
        print(result_music)
        return result_music
