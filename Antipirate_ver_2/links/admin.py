import asyncio
import difflib
from pathlib import Path
from subprocess import CalledProcessError
import requests
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
            music = asyncio.run(main_parser.main_process(links, deep=False, white_list=whitelist))
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

            import time
            from selenium.webdriver.support import expected_conditions
            from selenium.webdriver.support.wait import WebDriverWait
            import undetected_chromedriver as uc
            from selenium.webdriver.common.by import By
            import requests

            options = uc.ChromeOptions()
            options.arguments.extend(["--no-sandbox", "--disable-setuid-sandbox"])
            driver = uc.Chrome(options,
                               executable_path="/home/andrew/PycharmProjects/pythonProject1/driver/chromedriver")
            api_str = 'http://2captcha.com/in.php?key=3d5e22fb2f295276b486c08de4b6f19a&method=userrecaptcha&googlekey=6LeVK0AhAAAAAAM8ccCAZcaNBQbJQ-iZiZQxyG4h&json=1&pageurl=https://reportcontent.google.com/forms/dmca_search?hl=en&utm_source=wmx&utm_medium=deprecation-pane&utm_content=legal-removal-request'

            def api_call_loop(api_response):
                response = None
                while not response or not response.json()['status']:
                    response = requests.get(
                        f'http://2captcha.com/res.php?key=3d5e22fb2f295276b486c08de4b6f19a&action=get&json=1&id={api_response}')
                    if not response.json()['status']:
                        print(f'{response.json()} ... solving Captcha')
                        time.sleep(10)
                print(str(response.json()))
                return response.json()

            try:
                driver.get('https://accounts.google.com/servicelogin')
                time.sleep(0.05)

                driver.maximize_window()

                time.sleep(0.05)
                email_form = WebDriverWait(driver, 20).until(
                    expected_conditions.element_to_be_clickable((By.ID, "identifierId")))
                email_form.send_keys('andrew.sev87@gmail.com')
                time.sleep(0.05)

                next_button = driver.find_element(By.XPATH, '//*[@id="identifierNext"]/div/button/span')
                next_button.click()

                time.sleep(0.05)
                WebDriverWait(driver, 20).until(expected_conditions.element_to_be_clickable((By.NAME, "Passwd")))
                password_form = driver.find_element(By.NAME, 'Passwd')
                password_form.send_keys('731koshki29X')
                time.sleep(0.05)

                next_button = driver.find_element(By.XPATH, '//*[@id="passwordNext"]/div/button/span')
                next_button.click()

                time.sleep(2)

                driver.get('https://www.google.com/webmasters/tools/legal-removal-request?hl=en&pid=0&complaint_type=1')
                first_name = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                              '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[1]/gdf-text-input/material-input/label/input')))
                driver.execute_script('arguments[0].scrollIntoView(true);', first_name)
                first_name.send_keys('Joe')
                time.sleep(0.05)
                last_name = driver.find_element(By.XPATH,
                                                '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[2]/gdf-text-input/material-input/label/input')
                last_name.send_keys('Doe')
                time.sleep(0.05)
                country = driver.find_element(By.XPATH,
                                              '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[3]/gdf-text-input/material-input/label/input')
                country.send_keys('Company for test')
                time.sleep(0.05)
                confirm = driver.find_element(By.XPATH,
                                              '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[5]/gdf-checkbox/div/material-checkbox/div[1]/material-ripple').click()
                time.sleep(0.05)
                email = driver.find_element(By.XPATH,
                                            '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[6]/gdf-text-input/material-input/label/input')
                email.send_keys('email@test.com')
                time.sleep(0.05)

                button_no = driver.find_element(By.XPATH,
                                                '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[5]/div/div[2]/gdf-component/gdf-radio-buttons/fieldset/material-radio-group/material-radio[2]/div[1]/material-ripple').click()
                time.sleep(0.05)
                text_area_1 = driver.find_element(By.XPATH,
                                                  '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[6]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[1]/div/div[2]/gdf-component/gdf-textarea/material-input/label/span[2]/textarea')
                driver.execute_script('arguments[0].scrollIntoView(true);', text_area_1)
                text_area_1.send_keys('Test text')
                time.sleep(0.05)

                text_area_2 = driver.find_element(By.XPATH,
                                                  '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[6]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[2]/div/div[2]/gdf-component/gdf-textarea/material-input/label/span[2]/textarea')
                driver.execute_script('arguments[0].scrollIntoView(true);', text_area_2)
                text_area_2.send_keys('https://www.someresourse.com/')
                time.sleep(0.05)

                text_area_3 = driver.find_element(By.XPATH,
                                                  '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[6]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[2]/div/div[2]/gdf-container/div/div[2]/gdf-component/gdf-textarea/material-input/label/span[2]/textarea')
                driver.execute_script('arguments[0].scrollIntoView(true);', text_area_3)
                text_area_3.send_keys('https://www.someresourse.com/')
                time.sleep(0.05)

                consents = (
                    driver.find_element(By.XPATH,
                                        '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[7]/div/div[2]/gdf-component[1]/gdf-checkbox/div/material-checkbox/div[1]/material-ripple'),
                    driver.find_element(By.XPATH,
                                        '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[7]/div/div[2]/gdf-component[2]/gdf-checkbox/div/material-checkbox/div[1]/material-ripple'),
                    driver.find_element(By.XPATH,
                                        '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[7]/div/div[2]/gdf-component[3]/gdf-checkbox/div/material-checkbox/div[1]/material-ripple')
                )
                driver.execute_script('arguments[0].scrollIntoView(true);', consents[0])
                time.sleep(0.05)
                for c in consents:
                    c.click()
                time.sleep(0.05)

                date = driver.find_elements(By.TAG_NAME, 'dropdown-button')[1].click()
                time.sleep(1)
                today = driver.find_element(By.CSS_SELECTOR, 'div.day-slot.visible.today').click()
                time.sleep(0.05)

                signature = driver.find_element(By.XPATH,
                                                '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[8]/div/div[2]/gdf-component[2]/gdf-text-input/material-input/label/input')
                signature.send_keys('Joe Doe')

                api_call = requests.get(api_str)
                time.sleep(1)
                print(api_call.json())
                api_response_captcha_solver = api_call_loop(api_call.json()["request"])

                driver.execute_script('document.getElementById("g-recaptcha-response").removeAttribute("style");')
                time.sleep(0.05)
                driver.execute_script(
                    f'document.getElementById("g-recaptcha-response").innerHTML = {api_response_captcha_solver};')
                time.sleep(0.05)
                try:
                    driver.execute_script(f'onRecaptcha({api_response_captcha_solver});')
                    print("Captcha solved")
                except Exception:
                    driver.execute_script(f'onRecaptcha();')

                time.sleep(10)

            finally:
                driver.quit()

            return HttpResponseRedirect(".")
        return super().response_change(request, obj)

    list_display_links = ("link",)
    actions = (search_music, compare_music)
    readonly_fields = ('music', 'checked', 'music_found', 'music_links', "music_match")
    list_filter = ('music', 'checked', 'music_found', "music_match", "manual_check")
