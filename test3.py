from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

from bs4 import BeautifulSoup
from threading import Thread

import unicodedata
import pickle
import time
import json
import os
import platform
import re
import sys

from util import *

username = '15913'
password = '546609529'
base_url = 'https://hcc-tams.com.ph'

timeout = 9
tries = 6
sleep = 3

urls = {
    'overtime': 'OT',
    'officialbusiness': 'OB',
    'leave': 'LV'
}

output_dir = "tams"
cookie_path = f"{output_dir}/cookies_{username}.pkl"

class StealthChromeOptions(ChromeOptions):
    def __init__(self, headless: bool = True, timeout: int = timeout):
        super().__init__()

        args = (
            "--no-sandbox",
            "--disable-automation",
            "--disable-gpu",
            "--disable-infobars",
            "--disable-dev-shm-usage",
            "--disable-extensions",
            "--disable-blink-features=AutomationControlled",
            "--disable-timezone-tracking-option",
            "--disable-fine-grained-time-zone-detection",
            "--enable-auto-reload",
            "--enable-popup-blocking"
        )

        if headless:
            args += ("--headless=new")

        for arg in args:
            self.add_argument(arg)

        self.page_load_strategy = "eager"
        self.unhandled_prompt_behavior = "accept"
        self.accept_insecure_certs = True
        self.timeout = timeout
        self.add_experimental_option = {
            "excludeSwitches": ["enable-automation"],
            "useAutomationExtension": False
        }

    def build_user_agent():
        ua_tuple = (
            'Mozilla/5.0',
            '(%s; U; %s; en-us)' % (platform.platform(),
                                    platform.architecture()[0]),
            'Python/%s' % platform.python_version(),
            '(KHTML, like Gecko)',
            'speedtest-cli/%s' % __version__
        )
        user_agent = ' '.join(ua_tuple)
        return user_agent

def create_driver():
    options = Options()
    args = (
        "--no-sandbox",
        "--disable-gpu",
        "--disable-infobars",
        "--disable-dev-shm-usage",
        "--disable-extensions",
        "--disable-blink-features",
        "--disable-blink-features=AutomationControlled",
        "--disable-timezone-tracking-option",
        "--disable-fine-grained-time-zone-detection",
        "--enable-popup-blocking",
        "--headless=new"
    )
    
    for arg in args:
        options.add_argument(arg)

    options.page_load_strategy = "eager"
    options.unhandled_prompt_behavior = "accept"
    options.accept_insecure_certs = True
    
    for k, v in {
        "excludeSwitches": ["enable-automation"],
        "useAutomationExtension": False
    }.items():
        options.add_experimental_option(k, v)

    driver = webdriver.Chrome(options=options)
    driver.execute_cdp_cmd('Network.enable', {})
    driver.execute_cdp_cmd('Network.setBlockedURLs', {"urls": ["*.css"]})
    # driver.execute_cdp_cmd('Network.setUserAgentOverride', {"userAgent": 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/83.0.4103.53 Safari/537.36'})
    # driver.execute_script("Object.defineProperty(navigator, 'webdriver', {get: () => undefined})")
    return driver

def normalize(text):
    text = str(text)
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'\s+,', ',', text)
    text = unicodedata.normalize("NFKC", text)  # Normalize unicode
    text = text.replace('\xa0', ' ')  # Replace non-breaking spaces
    text = re.sub(r'[\u200b\ufeff]', '', text)  # Remove invisible chars
    text = text.replace('Approver', ' Approver')
    return text.strip()
    
def delete_file(path: str | None = None) -> None:
    if path and os.path.exists(path):
        os.remove(path)

def save_cookies(driver, path: str | None = None) -> None:
    path = path or cookie_path
    with open(path, 'wb') as file:
        pickle.dump(driver.get_cookies(), file)

def load_cookies(driver, path: str | None = None) -> None:
    path = path or cookie_path
    with open(path, 'rb') as file:
        cookies = pickle.load(file)
        for cookie in cookies:
            driver.add_cookie(cookie)
    driver.refresh()
    
def waitfor(driver, value='table', by=By.TAG_NAME):
    try:
        el = WebDriverWait(driver, timeout).until(EC.presence_of_element_located((by, value)))
        return el if el else None
        
    except Exception as e:
        print(e)
    
    
def login(driver) -> None:
    if "Auth" not in driver.current_url:
        driver.get(f"{base_url}/tams/Auth")
    
    loginform = waitfor(driver, 'login-form', By.ID)
    if loginform:
        driver.find_element(By.NAME, 'username').send_keys(username)
        driver.find_element(By.NAME, 'password').send_keys(password)
        driver.find_element(By.XPATH, ".//button[@type='submit']").click()
        
        user = waitfor(driver, 'lastname', By.ID)
        if user:
            print(f'Logged in as [{normalize(user.get_attribute("value"))}]')

def login_if_needed(driver) -> None:
    driver.get(f"{base_url}/")
    
    if os.path.exists(cookie_path):
        for i in range(retries):
            print(f"Trying to load cookies ({i+1}/{tries})...")
            load_cookies(driver, cookie_path)
            if "Auth" not in driver.current_url:
                return  # Logged in successfully using cookies
    
    login(driver)
    save_cookies(driver)
    
def build_user_agent():
    ua_tuple = (
        'Mozilla/5.0',
        '(%s; U; %s; en-us)' % (platform.platform(),
                                platform.architecture()[0]),
        'Python/%s' % platform.python_version(),
        '(KHTML, like Gecko)'
    )
    user_agent = ' '.join(ua_tuple)
    return user_agent

def scrape_table(url):
    driver = create_driver()
    try:
        login_if_needed(driver)
        driver.get(f'{base_url}/tams/filing/{url}')

        data = []
        headers = []
        keep_indices = []

        for i in range(tries):
            print(f"Scraping [{urls[url]}] table ({i+1}/{tries})...")

            WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.TAG_NAME, 'table')))
            time.sleep(sleep)

            soup = BeautifulSoup(driver.page_source, "html.parser")
            table = soup.select_one('table')

            if not table:
                print(f"Error: [{urls[url]}] table not found.")
                return

            if not headers:
                ths = table.select("thead th")
                headers = [normalize(th.get_text(strip=True)) for th in ths if normalize(th.get_text(strip=True)) not in ("Action", "Attachment")]
                keep_indices = [i for i, th in enumerate(ths) if normalize(th.get_text(strip=True)) not in ("Action", "Attachment")]

            for row in table.select("tbody tr"):
                tds = row.select("td")
                cells = [normalize(tds[i].get_text(strip=True)) for i in keep_indices if i < len(normalize(tds))]
                data.append(dict(zip(headers, cells)))

            try:
                next_btn = driver.find_element(By.XPATH, '//a[text()="Next"]')
                if 'disabled' in next_btn.get_attribute('class'):
                    break
                next_btn.click()
                time.sleep(sleep)
                
            except Exception:
                break  # No Next button or can't click it, likely last page

        if data:
            with open(os.path.join(output_dir, f'{url}-data.json'), 'w') as f:
                json.dump(data, f, indent=2)
            print(f"Scraped {len(data)} rows from [{urls[url]}] table.")
        else:
            print(f"Failed to scrape [{urls[url]}] table.")

    except Exception as e:
        print(f"Error in [{urls[url]}] thread:\n{e}")
        
    finally:
        driver.quit()

def main():
    os.makedirs(output_dir, exist_ok=True)
    threads = []
    for url in urls.keys():
        t = Thread(target=scrape_table, args=(url,))
        t.start()
        threads.append(t)

    for t in threads:
        t.join()
        
if __name__ == "__main__":
    main()