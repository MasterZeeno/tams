import os
import json
import requests
import time
import shlex
import sys

from utils import print_success, print_error, print_warning, normalize, date_to_int, resolve_path, sort_data, get_date

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

from urllib.parse import urljoin

sort_key = "timestamp"
timeout = 9
retries = 6
sleep = 0.69

def set_global(name, value):
    globals()[name] = value
    
def parse_args(args):
    try:
        pairs = shlex.split(args)
        return dict(pair.split('=', 1) for pair in pairs if '=' in pair)
    except ValueError as e:
        print(f"Error parsing arguments: {e}")
        return {}
    
def init_params(args):
    set_global("params", parse_args(args))
    set_global("login_inputs", {})
    for key, value in params.items():
        set_global(key, value)
        if key != "homepage":
            login_inputs[key] = value
    set_global("base_url", f"{homepage}/tams/")
    set_global("months", [])
    set_global("current_month", get_date("month"))
    set_global("current_year", get_date("year"))
    for i in range(1, 13):
        date_val = f"{current_year}-{i:02}-01"
        dt = datetime.strptime(date_val, "%Y-%m-%d")
        months.append(dt.strftime("%B"))
    set_global("filling_url_list", ["overtime", "officialbusiness", "leave"])
    set_global("url_list", filling_url_list)
    url_list.append("attendance")
    
def abort(msg="Aborted"):
    print_error(msg)
    if driver:
        driver.quit()
    sys.exit(1)

def init():
    init_params()

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
        driver.execute_cdp_cmd('Network.enable', {})
        driver.execute_cdp_cmd('Network.setBlockedURLs', {
            "urls": ["*.css"]
        })
    except WebDriverException as e:
        abort(f"WebDriver error: {e}")
    except Exception as e:
        abort(f"Unexpected error: {e}")

def check_internet(url=None):
    url = url or homepage

    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if status_code == 200:
                print_success("Internet connection verified")
                return True
            else:
                abort(f"Attempt {attempt}/{retries} failed: status code: {status_code}")
        except requests.ConnectionError as e:
            abort(f"Attempt {attempt}/{retries} failed: Connection error: {e}")
        except requests.Timeout:
            abort(f"Attempt {attempt}/{retries} failed: Request timed out")
        
        if attempt < retries:
            print_warning("Retrying in 1 second...")
            time.sleep(sleep)
            
    abort("Failed to establish internet connection after multiple attempts")

def navigate(url):
    if any(k in url.lower() for k in filling_url_list):
        full_url = urljoin(base_url, f"filing/{url}")
    else:
        full_url = urljoin(base_url, url)
    
    try:
        driver.get(full_url)
    except Exception as e:
        abort(f"Error navigating to {full_url}: {e}")

def define_table(url):
    navigate(url)
    set_global("table_data", [])
    
    for el_name in ["table", "tbody", "tr", "thead", "th"]:
        if "tr" in el_name:
            el_parent = tbody
        elif "th" in el_name:
            el_parent = thead
        else:
            el_parent = table
        
        element = find_element(
            parent=el_parent, by=By.TAG_NAME, locator=el_name,
            True if "tr" in el_name or "th" in el_name else False
        )
        
        if not element:
            print_warning(f"Element '{el_name.title()}' not found")
            return table_data
            
        set_global(el_name, element)
        
    set_global("headers", [h.text.strip().replace('\n', ' ').replace(' ', '_').lower() for h in th])
    

def scrape_table_data(url):
    define_table(url)
    
    for r in tr:
        cells = find_element(r, by=By.TAG_NAME, locator="td", multiple=True)
        if not cells:
            continue

        cells = [normalize(cell.text) for cell in cells]
        row_data = {
            header: cell
            for header, cell in zip(headers, cells)
            if "action" not in header and "attachment" not in header and "_id" not in header
        }

        if url == "attendance":
            index = "date"
        elif url == "overtime":
            index = "date_from"
        else:
            index = "duration"

        table_data.append({ sort_key: date_to_int(row_data.get(index, 0)), **row_data })
    
    return table_data

def to_proper(string=None):
    if not string:
        return ""
    return str(string).strip().title()
    
def null_err_msg(msg=None, by=None, post_msg=None, x=False, ret=None, locator=None):
    final_msg = "Error"
    if msg:
        if locator is None:
            locator = "element"
        final_msg += f": {to_proper(msg)} [{to_proper(locator)}]"
    if by:
        final_msg += f", by [{to_proper(by)}]"
    if post_msg:
        final_msg += f"\n\n{to_proper(post_msg)}"
    if x:
        abort(final_msg)
    else:
        print_warning(final_msg)

    return ret if isinstance(ret, bool) else None
    
def find_element(parent=None, by=By.ID, locator=None, multiple=False):
    if locator is None:
        print_warning("Locator must be provided")
        return None
        
    if parent is None:
        parent = driver
        
    if multiple:
        condition = EC.presence_of_all_elements_located((by, locator))
    else:
        condition = EC.presence_of_element_located((by, locator))
        
    try:
        element = WebDriverWait(parent, timeout).until(condition)
        if element is not None:
            return element

    except TimeoutException:
        return null_err_msg(msg="timedout", locator=locator, by=by)
    except NoSuchElementException:
        return null_err_msg(msg="not found", locator=locator, by=by)
    except Exception as e:
        return null_err_msg(locator=locator, by=by, post_msg=e)
        
def process_element(parent=None, by, locator, action=None, value=None, x=False):
    el = process_el(parent, by, locator)
    
    if el is not None:
        if action is None:
            return el
            
        if "click" in action:
            el.click()
        elif "send" in action:
            if value is not None:
                el.clear()
                el.send_keys(str(value))
                
        time.sleep(sleep)
    else:
        return null_err_msg(msg="not found", locator=locator, x=True, ret=False)

def login():
    navigate("Auth")
    
    try:
        login_form = process_element(by=By.ID, locator="login-form")

        for key, value in params.items():
            if key != "homepage":
                process_element(login_form, by=By.NAME, locator=key, action="send", value=value, x=True):

        if not click_element(login_form, by=By.XPATH, locator=".//button[@type='submit']"):
            login_form.submit()
        
        set_global("full_name", normalize(find_element(by=By.ID, locator="lastname").get_attribute("value")))
        
        if full_name:
            print_success(f"Logged in as: [{full_name}]")
        else:
            abort("Login failed: 'lastname' element not found")
    
    except Exception as e:
        abort(f"Failed to login: {e}")


def main():
    init()

    try:
        if not check_internet():
            abort("No internet connection. Please check your connection and try again")
         
        login()
    
        main_table_data = {}
        
        for url in url_list:
            navigate(url)
            table_data = []
            
            if "attendance" in url.lower():
                for increment in range(-1, 2):  # -1, 0, 1 for previous, current, and next month
                    if process_element(by=By.ID, locator="month", action="click", x=True):
                        
                        adjusted_month = (current_month + increment - 1) % 12 + 1
                        adjusted_year = current_year
                        
                        # Adjust the year if the month rolls over
                        if adjusted_month == 12 and increment == -1:
                            adjusted_year -= 1  # Previous December -> Decrement year
                        elif adjusted_month == 1 and increment == 1:
                            adjusted_year += 1  # Next January -> Increment year
                            
                        selected_month = months[adjusted_month - 1]
                        
                        process_element(parent=month_select, by=By.XPATH, locator=f".//option[contains(text(), '{selected_month}')]", action="click")
                        process_element(by=By.NAME, locator="year", action="send", value=adjusted_year, x=true)
                        process_element(by=By.XPATH, locator="//button[@type='submit' and contains(text(), 'Search')]", action="click")
  
                        scraped_data = scrape_table_data(url)
                        if scraped_data:
                            table_data.append(sort_data(scraped_data, sort_key))
     
            else:
                scraped_data = scrape_table_data(url)
                if scraped_data:
                    table_data.append(sort_data(scraped_data, sort_key))
            
            if table_data:
                flattened = [item for data in table_data for item in data]
                main_table_data[url] = flattened
                print_success(f"Scrapped: [{url.title()}] table")
                
        if main_table_data:
            json_path = resolve_path(f"{username}.json")
            # json_path = f"{userdata_path}/{username}.json" # os.path.join(userdata_path, f"{username}.json")
            
            try:
                with open(json_path, 'w') as json_file:
                    json.dump(main_table_data, json_file, indent=2)
                    
                # relative_path = os.path.relpath(json_path, os.getcwd())
                print_success(f"Saved: {username}.json")
            except OSError as e:
                abort(f"Error saving data to file: {e}")
        else:
            abort("No data collected from any of the URLs")
    
    finally:
        abort()

if __name__ == "__main__":
    main()
