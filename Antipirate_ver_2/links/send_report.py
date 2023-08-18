import time

from selenium import webdriver
from selenium.webdriver import Keys
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support import expected_conditions
from selenium.webdriver.support.wait import WebDriverWait
import undetected_chromedriver as uc
from selenium.webdriver.common.by import By
import requests


def api_call_loop(api_response):
    response = None
    while not response or not response.json()['status']:
        response = requests.get(
            f'http://2captcha.com/res.php?key=2d426bb5162a1e697572a5e8c3126f2e&action=get&json=1&id={api_response}')
        if not response.json()['status']:
            print(f'{response.json()} ... solving Captcha')
            time.sleep(10)
    print(str(response.json()))
    return response.json()


def send_report_selenium(obj):
    # options = uc.ChromeOptions()
    options = webdriver.ChromeOptions()
    options.add_argument("--no-sandbox")
    user_data_dir = "/home/andrew/.config/google-chrome"  # Pointing to the main user data directory
    profile_directory = "Profile 7"  # The specific profile folder

    options.add_argument(r"--user-data-dir=/home/andrew/.config/google-chrome")
    options.add_argument(r"--profile-directory=Profile 7")
    # options.add_argument("--disable-gpu")
    # options.add_argument("--no-sandbox")
    # options.add_argument("--disable-setuid-sandbox")
    # options.add_argument("--remote-debugging-port=9222")
    #options.add_argument('--headless')

    options.binary_location = "/usr/bin/google-chrome"
    # Start the driver
    driver = webdriver.Chrome(
        #executable_path='/home/andrew/chromedriver/chromedriver',
        options=options)
    time.sleep(2)

    driver.get('https://www.google.com')
    time.sleep(2)
    driver.save_screenshot("screenshot.png")

    # driver = uc.Chrome(options, headless=True,
    #                    executable_path="/home/andrew/PycharmProjects/pythonProject1/driver/chromedriver")
    api_str = 'http://2captcha.com/in.php?key=2d426bb5162a1e697572a5e8c3126f2e&method=userrecaptcha&googlekey=6LeVK0AhAAAAAAM8ccCAZcaNBQbJQ-iZiZQxyG4h&json=1&pageurl=https://reportcontent.google.com/forms/dmca_search?hl=en&utm_source=wmx&utm_medium=deprecation-pane&utm_content=legal-removal-request'

    try:
        driver.get('https://www.google.com/webmasters/tools/legal-removal-request?hl=en&pid=0&complaint_type=1')
        first_name = WebDriverWait(driver, 20).until(expected_conditions.presence_of_element_located((By.XPATH,
                                                                                                      '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[1]/gdf-text-input/material-input/label/input')))
        driver.execute_script('arguments[0].scrollIntoView(true);', first_name)
        first_name.send_keys('Viacheslav')
        time.sleep(0.05)
        last_name = driver.find_element(By.XPATH,
                                        '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[2]/gdf-text-input/material-input/label/input')
        last_name.send_keys('Sen')
        time.sleep(0.05)
        country = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[3]/gdf-text-input/material-input/label/input')
        country.send_keys('ELSP Company LLC')
        time.sleep(0.05)
        confirm = driver.find_element(By.XPATH,
                                      '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[6]/gdf-checkbox/div/material-checkbox/div[1]/material-ripple').click()
        time.sleep(0.05)
        email = driver.find_element(By.XPATH,
                                    '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[4]/div/div[2]/gdf-component[7]/gdf-text-input/material-input/label/input')
        email.send_keys('elspcompany@gmail.com')
        time.sleep(0.05)

        driver.find_element(By.XPATH,
                            '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[5]/div/div[2]/gdf-component/gdf-radio-buttons/fieldset/material-radio-group/material-radio[2]/div[1]/material-ripple').click()
        time.sleep(0.05)
        text_area_1 = driver.find_element(By.XPATH,
                                          '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[6]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[1]/div/div[2]/gdf-component/gdf-textarea/material-input/label/span[2]/textarea')
        driver.execute_script('arguments[0].scrollIntoView(true);', text_area_1)
        text_area_1.send_keys(f'Audio work in form of the music track, title: "{obj.music}", exclusively belonging to us')
        time.sleep(0.05)
        driver.save_screenshot("screenshot22.png")

        text_area_2 = driver.find_element(By.XPATH,
                                          '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[6]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[2]/div/div[2]/gdf-component/gdf-textarea/material-input/label/span[2]/textarea')
        driver.execute_script('arguments[0].scrollIntoView(true);', text_area_2)
        # text_area_2.send_keys(f'{obj.music.link}')
        driver.execute_script(f"arguments[0].value = '{obj.music.link}'", text_area_2)
        text_area_2.send_keys(Keys.SPACE)
        text_area_2.send_keys(Keys.BACK_SPACE)
        time.sleep(0.05)

        text_area_3 = driver.find_element(By.XPATH,
                                          '/html/body/div[1]/root/div/main/chip-form/div/span/gdf-form/form/gdf-container[6]/div/div[2]/gdf-container[1]/div/div[2]/gdf-container[2]/div/div[2]/gdf-container/div/div[2]/gdf-component/gdf-textarea/material-input/label/span[2]/textarea')
        driver.execute_script('arguments[0].scrollIntoView(true);', text_area_3)
        # text_area_3.send_keys(f'{obj.link}')
        driver.execute_script(f"arguments[0].value = '{obj.link}'", text_area_3)
        text_area_3.send_keys(Keys.SPACE)
        text_area_3.send_keys(Keys.BACK_SPACE)
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
        signature.send_keys('Viacheslav Sen')

        api_call = requests.get(api_str)
        time.sleep(1)
        print(api_call.json())
        api_response_captcha_solver = api_call_loop(api_call.json()["request"])
        api_response_captcha_solver = api_response_captcha_solver["request"]

        driver.execute_script('document.getElementById("g-recaptcha-response").removeAttribute("style");')
        time.sleep(0.05)
        driver.execute_script(
            f'document.getElementById("g-recaptcha-response").innerHTML = "{api_response_captcha_solver}";')
        time.sleep(0.05)
        try:
            driver.execute_script(f'onRecaptcha("{api_response_captcha_solver}");')
            print("Captcha solved")
        except Exception:
            driver.execute_script(f'onRecaptcha();')
        driver.save_screenshot("screenshot33.png")

        time.sleep(1)
        driver.execute_script("window.focus();")
        button = driver.find_element(By.XPATH, '/html/body/div[1]/root/div/main/chip-form/div/span/div/button')
        driver.execute_script("arguments[0].removeAttribute('disabled')", button)

        time.sleep(40)

    finally:
        driver.quit()
