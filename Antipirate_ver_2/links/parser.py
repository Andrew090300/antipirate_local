import asyncio
import random
import time
from ssl import SSLCertVerificationError
from typing import Union
from aiohttp import (
    ClientConnectorSSLError,
    ClientSession,
    ClientConnectorError,
    ClientResponseError,
    ClientOSError, ServerDisconnectedError)
from aiolimiter import AsyncLimiter
from bs4 import BeautifulSoup, SoupStrainer
from urllib.parse import urlencode, urljoin
from requests import Response, RequestException
from requests_html import HTMLSession

from Antipirate_ver_2.core.models import Core
from Antipirate_ver_2.utils import user_agent
from Antipirate_ver_2.utils.unwanted_domains import google_domains
from Antipirate_ver_2.whitelist.models import WhiteListDomain


class GoogleParser:
    @staticmethod
    def get_source(payload: dict) -> Response:
        params = urlencode(payload)
        headers = {'User-Agent': random.choice(user_agent.user_agent)}
        url = f'https://www.google.com/search?{params}'

        try:
            session = HTMLSession()
            time.sleep(1)

            response = session.get(url=url, headers=headers)
            return response

        except RequestException as e:
            print(e)

    @staticmethod
    def scrape_google(query: str) -> list:
        pages = Core.objects.first().pages_number
        pages = 10 if pages is None else pages
        payload = {
            'q': query,
            # 'uule': 'code',  # This is location code. Will figure out later
        }

        result_links = []
        counter = 1
        for count in range(0, pages * 10, 10):
            print(f'Google Page {counter} is processed')
            counter += 1
            payload['start'] = count  # One page is equal to 10 google results.
            time.sleep(0.01)
            response = GoogleParser.get_source(payload)
            try:
                links = list(response.html.absolute_links)
                for url in links[:]:
                    if url.startswith(google_domains + tuple(WhiteListDomain.objects.values_list(
                            'domain', flat=True).distinct())):
                        links.remove(url)
                result_links.extend(links)
            except AttributeError as e:
                print(e)
        return result_links


class AsyncParser:
    def __init__(self):
        self.limiter = AsyncLimiter(1, 0.125)
        self.headers = {'User-Agent': random.choice(user_agent.user_agent)}
        self.links = []
        self.counter = 0  # To be removed in production
        self.music_count = 0
        self.all_music = {}
        self.performance_time = time.perf_counter()  # To be removed in production

    def get_data(self, html_text: bytes, parsed_url: str, deep) -> list:
        soup = BeautifulSoup(html_text, 'lxml', parse_only=SoupStrainer('a', href=True))
        link_obj = soup.find_all('a')

        # Links generator
        def gen():
            for link in link_obj:
                try:
                    href = link.attrs['href'].strip()
                    if href and not href.startswith(('#', 'javascript:', 'tel', 'mailto:')):
                        yield href
                except KeyError:
                    pass

        elems = set(gen())

        for _link in elems:
            abs_link = urljoin(parsed_url, _link)
            if abs_link[-4:] in ('.mp3',
                                 '.mp4',
                                 '.aiff',
                                 '.flac',
                                 '.m4a',
                                 '.wav',
                                 '.ogg',):
                self.music_count += 1
                if not self.all_music.get(parsed_url, ):
                    self.all_music[parsed_url] = []
                self.all_music[parsed_url].append(abs_link)
                print(f'Total Music Count: {self.music_count}')
            if not deep:
                self.links.append(abs_link)

        # TODO Remove print in production
        print(f'Total links found: {len(self.links)}')
        if not deep:
            return self.links

    async def get_links(self, url: str, semaphore: asyncio.Semaphore, deep) -> Union[list, None]:
        async with ClientSession(headers=self.headers) as session:
            await semaphore.acquire()
            async with self.limiter:
                # TODO Remove print in production
                print(f"Begin reading {url} {(time.perf_counter() - self.performance_time):0.4f} seconds")

                try:
                    async with session.get(url, timeout=10, ssl=False) as resp:
                        self.counter += 1
                        if resp.status != 200:
                            print(f'Invalid response on {url} - {resp.status}')
                        content = await resp.read()
                        semaphore.release()
                        print(f'Counter: __{self.counter}')
                        return self.get_data(content, url, deep)
                except (SSLCertVerificationError,
                        ClientResponseError,
                        ClientConnectorSSLError,
                        ClientConnectorError,
                        ClientOSError,
                        ServerDisconnectedError,
                        asyncio.exceptions.TimeoutError) as e:
                    print(e)

    async def main_process(self, array: list, deep: bool, white_list: tuple) -> dict:
        tasks = []
        semaphore = asyncio.Semaphore(value=10)
        for item in array:
            if not item.startswith(white_list) and not item[-4:] == ':443' and item.startswith('http'):
                tasks.append(self.get_links(item, semaphore, deep))
        try:
            await asyncio.wait_for(asyncio.gather(*tasks), 1000)
        except asyncio.exceptions.TimeoutError as e:
            print(f'Timeout {e}')
        # TODO Remove counters and print in production
        elapsed = time.perf_counter() - self.performance_time
        print(f'Total {self.music_count} mp3 files found on {len(self.all_music)} websites')
        print(f"Execution time: {elapsed:0.2f} seconds.")
        if not deep:
            return self.all_music
