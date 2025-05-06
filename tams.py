import os
import json
import re
import requests
import sys
import shlex
import time

from utils import print_success, print_error, print_warning

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException
from urllib.parse import urljoin
from datetime import datetime

global_timeout = 10

months = ["January", "February", "March", "April", "May", "June",
    "July", "August", "September", "October", "November", "December"]

def set_global(name, value):
    globals()[name] = value

def parse_args():
    try:
        pairs = shlex.split(' '.join(sys.argv[1:]))
        return dict(pair.split('=', 1) for pair in pairs if '=' in pair)
    except ValueError as e:
        print(f"Error parsing parameters: {e}")
        return {}

def init():
    set_global("params", parse_args())
    for key, value in params.items():
        set_global(key, value)

    # Setup the Chrome options
    options = webdriver.ChromeOptions()

    args=(
        "--no-sandbox",
        "--disable-dev-shm-usage",
        "--display=:1",
        "--start-maximized",
        "--disable-extensions",
        "--disable-fine-grained-time-zone-detection",
        "--headless=new"
    )

    for arg in args:
        options.add_argument(arg)

    options.page_load_strategy = "eager"
    options.unhandled_prompt_behavior = "accept"
    options.accept_insecure_certs = True

    load_timeout = global_timeout * 1000
    for type in ["pageLoad", "implicit"]:
        options.timeouts = { type: load_timeout }


    # Optional: Specify the path to the ChromeDriver if not in PATH
    # DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "path/to/chromedriver")
    # driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)

    try:
        set_global("driver", webdriver.Chrome(options=options))
    except WebDriverException as e:
        print_error(f"WebDriver error: {e}")
        sys.exit(1)
    except Exception as e:
        print_error(f"Unexpected error: {e}")
        sys.exit(1)

# Function to convert date string to timestamp for sorting
def date_to_int(date_str):
    if not isinstance(date_str, str):
        date_str = str(date_str)

    try:
        date_part = re.split(r"[,\s]+", date_str.strip())[0]
        dt = datetime.strptime(date_part, "%Y-%m-%d")
        return int(dt.timestamp())
    except ValueError:
        return 0

# Sort the data based on the timestamp in descending order
def sort_by_timestamp(data):
    return sorted(data, key=lambda x: int(x.get("timestamp", 0)))

def check_internet(url=None, timeout=global_timeout, retries=3):
    url = url or homepage

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                print_success("Internet connection verified")
                return True
            else:
                print_error(f"Received unexpected status code: {response.status_code}")
        except requests.ConnectionError as e:
            print_error(f"Attempt {attempt}/{retries} failed: Connection error: {e}")
        except requests.Timeout:
            print_error(f"Attempt {attempt}/{retries} failed: Request timed out")
        
        if attempt < retries:
            print_warning("Retrying in 1 second...")
            time.sleep(1)
    print_error("Failed to establish internet connection after multiple attempts")
    sys.exit(1)

def navigate(url):
    new_url = f"{homepage}/tams/"

    if any(keyword in url.lower() for keyword in ["overtime", "officialbusiness", "leave"]):
        full_url = urljoin(new_url, f"filing/{url}")
    else:
        full_url = urljoin(new_url, url)
    
    try:
        driver.get(full_url)
    except Exception as e:
        print_error(f"Error navigating to {full_url}: {e}")
        sys.exit(1)

def validate_and_create_path(path=None):
    path = path or os.path.join(os.environ.get('PWD', ''), 'USERDATA')
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        print_error(f"Error creating directory '{path}': {e}")
        driver.quit()
        sys.exit(1)
    return path

def scrape_table_data(url):
    table_data = []
    table = process_element(by=By.TAG_NAME, locator="table")
    if not table:
        print_error("Table not found")
        return table_data
    
    header = process_element(table, by=By.TAG_NAME, locator="thead")
    if not header:
        print_error("Table header not found")
        return table_data
    
    header_elems = process_element(header, by=By.TAG_NAME, locator="th", multiple=True)
    if not header_elems:
        print_error("Table headers not found")
        return table_data
    
    headers = [header.text.strip().replace('\n', ' ').replace(' ', '_').lower() for header in header_elems]
    
    tbody = process_element(table, by=By.TAG_NAME, locator="tbody")
    if not tbody:
        print_error("Table body not found")
        return table_data
    
    rows = process_element(tbody, by=By.TAG_NAME, locator="tr", multiple=True)
    if not rows:
        return table_data
    
    for row in rows:
        cells = process_element(row, by=By.TAG_NAME, locator="td", multiple=True)
        if not cells:
            continue

        cells = [cell.text.strip() for cell in cells]
        row_data = {
            header: cell
            for header, cell in zip(headers, cells)
            if "action" not in header and "attachment" not in header and "_id" not in header
        }

        if url == "attendance":
            index = "date"
        elif url == "officialbusiness":
            index = "duration"
        else:
            index = "date_from"

        row_data = { "timestamp": date_to_int(row_data.get(index, 0)), **row_data }

        table_data.append(row_data)
    
    return table_data

def process_element(parent=None, by=By.ID, locator=None, multiple=False, timeout=global_timeout):
    if locator is None:
        print_error("Locator must be provided")
        return None
        
    if parent is None:
        parent = driver
        
    try:
        if multiple:
            elements = WebDriverWait(parent, timeout).until(
                EC.presence_of_all_elements_located((by, locator))
            )
            return elements
        else:
            element = WebDriverWait(parent, timeout).until(
                EC.presence_of_element_located((by, locator))
            )
            return element
    except TimeoutException:
        return None
    except NoSuchElementException:
        print_warning(f"Element not found: {locator} by {by}")
        return None
    except Exception as e:
        print_error(f"Error processing element '{locator}' by {by}: {e}")
        return None

def normalize_spaces(text):
    if not isinstance(text, str):
        text = str(text)
    # Collapse all whitespace into single spaces
    text = re.sub(r'\s+', ' ', text.strip())
    # Remove space before commas
    text = re.sub(r'\s+,', ',', text)
    return text

def login():
    try:
        # Assuming login-form is identified by ID; adjust as needed
        login_form = process_element(by=By.ID, locator="login-form")
        if not login_form:
            print_error("Login form not found")
            driver.quit()
            sys.exit(1)
        
        for key, value in params.items():
            if key != "homepage":
                el = process_element(login_form, by=By.NAME, locator=key)
                if not el:
                    print_error(f"Login input '{key}' not found")
                    driver.quit()
                    sys.exit(1)
                el.clear()
                el.send_keys(value)

        # Submit the form; assuming there's a submit button
        submit_button = process_element(login_form, by=By.XPATH, locator=".//button[@type='submit']")
        if submit_button:
            try:
                submit_button.click()
            except ElementClickInterceptedException:
                login_form.submit()
        else:
            login_form.submit()
        
        # Wait for login success, e.g., presence of lastname element
        full_name = normalize_spaces(process_element(by=By.ID, locator="lastname").get_attribute("value"))
        if full_name:
            print_success(f"Logged in as: [{full_name}]")
        else:
            print_error("Login failed: 'lastname' element not found")
            driver.quit()
            sys.exit(1)
    
    except Exception as e:
        print_error(f"Failed to login: {e}")
        driver.quit()
        sys.exit(1)


def main():
    init()

    try:
        if not check_internet():
            print_error("No internet connection. Please check your connection and try again")
            driver.quit()
            sys.exit(1)
        
        navigate("Auth")
        login()
    
        url_list = ["attendance", "overtime", "officialbusiness", "leave"]
        main_table_data = {}
        
        for url in url_list:
            navigate(url)
            table_data = []
            
            if "attendance" in url.lower(): 
                current_month = datetime.now().month
                current_year = datetime.now().year
                    
                for increment in range(-1, 2):  # -1, 0, 1 for previous, current, and next month
                    month_select = process_element(by=By.ID, locator="month")  
                    year_input = process_element(by=By.NAME, locator="year")
                    
                    if month_select is not None and year_input is not None:
                        adjusted_month = (current_month + increment - 1) % 12 + 1
                        adjusted_year = current_year
                        
                        # Adjust the year if the month rolls over
                        if adjusted_month == 12 and increment == -1:
                            adjusted_year -= 1  # Previous December -> Decrement year
                        elif adjusted_month == 1 and increment == 1:
                            adjusted_year += 1  # Next January -> Increment year
                            
                        selected_month = months[adjusted_month - 1]

                        # Select the month
                        try:
                            month_select.click()
                        except Exception as e:
                            print_error(f"Error clicking month selector: {e}")
                            continue
                        
                        # Corrected XPath by adding the missing closing parenthesis
                        month_option = process_element(
                            parent=month_select, 
                            by=By.XPATH,
                            locator=f".//option[contains(text(), '{selected_month}')]"
                        )
                        if month_option is not None:
                            try:
                                month_option.click()
                            except Exception as e:
                                print_error(f"Error selecting month '{selected_month}': {e}")
                                continue
                        else:
                            print_warning(f"Month option '{selected_month}' not found")
                            continue
    
                        # Set the year; using send_keys instead of setting value directly
                        try:
                            year_input.clear()
                            year_input.send_keys(str(adjusted_year))
                        except Exception as e:
                            print_warning(f"Error setting year '{adjusted_year}': {e}")
                            continue
                            
                        # Click the search button
                        search_btn = process_element(by=By.XPATH, locator="//button[@type='submit' and contains(text(), 'Search')]")
                        if search_btn is not None:
                            try:
                                search_btn.click()
                                # Optionally, wait for the table to reload
                                time.sleep(2)  # Adjust as needed or use explicit waits
                            except Exception as e:
                                print_warning(f"Error clicking search button: {e}")
                                continue
                        else:
                            print_warning("Search button not found")
                            continue
                        
                        # Scrape table data for the selected month and year
                        scraped_data = scrape_table_data(url)
                        if scraped_data:
                            table_data.append(sort_by_timestamp(scraped_data))
                    else:
                        print_error("Month selector or year input not found")
            else:
                scraped_data = scrape_table_data(url)
                if scraped_data:
                    table_data.append(sort_by_timestamp(scraped_data))
            
            if table_data:
                flattened = [item for data in table_data for item in data]
                main_table_data[url] = flattened
                print_success(f"Scrapped: [{url.title()}] table")
                
        if main_table_data:
            userdata_path = validate_and_create_path()
            json_path = os.path.join(userdata_path, f"{username}.json")
            
            try:
                with open(json_path, 'w') as json_file:
                    json.dump(main_table_data, json_file, indent=2)
                    
                relative_path = os.path.relpath(json_path, os.getcwd())
                print_success(f"Saved: {relative_path}")
            except OSError as os_err:
                print_error(f"Error saving data to file: {os_err}")
        else:
            print_error("No data collected from any of the URLs")
    
    finally:
        driver.quit()

if __name__ == "__main__":
    main()