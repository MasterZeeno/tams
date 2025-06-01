import os
import random
import re
import requests
import shlex
import sys
import time
from datetime import datetime
from urllib.parse import urljoin

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException, ElementClickInterceptedException

# def navigate(url):
    # if any(k in url for k in url_list[1:]):
        # full_url = urljoin(base_url, f"filing/{url}")
    # else:
        # full_url = urljoin(base_url, url)
        
    # base_msg = "navigating"
    # for style, msg in {
        
    # }
    # print_msg(4, "𝒊", f"{base_msg}...", "a;b")
    
    # for attempt in range(1, retries + 1):
        # try:
            # driver.get(full_url)
        # except Exception:
            # s = "d"
            # for style, msg in {
                # f"b;{s}": f"Error {base_msg}",
                # f"{s};i;x": f"[{full_url}]"
            # }
            # print_error("Error navigating to:", "b;d")
        
        # if attempt < retries:
            # print_error(f"Retrying ({attempt}/{retries})...", "d;i;x")
            
            # s = "d"
            # for style, msg in {
                # f"b;{s}": err_msg,
                # f"{s};i;x": f"Retrying ({attempt}/{retries})..."
            # }.items():
                # print_error(msg, style)
            # time.sleep(interval)
        
    # abort(f"Error navigating to {full_url}")
        

def rnd_num():
    min_val = -(sleep/retries)
    max_val = sleep*(retries*sleep)
    
    return random.uniform(min_val, max_val)

def check_internet(url=None):
    print_msg(4, "𝒊", "Checking internet connection...", "a;b")
    
    url = url or homepage
    intervals = [round(sleep + rnd_num(), retries) for _ in range(retries)]
    
    for attempt in range(1, retries + 1):
        interval = intervals[attempt-1]
        ret_msg = f"Retrying in {int(interval*1000)} milliseconds..."
        err_msg = f"Attempt ({attempt}/{retries}) failed: "
        
        try:
            response = requests.get(url, timeout=timeout)
            status_code = response.status_code
            
            if status_code == 200:
                print_success("Internet connection verified")
                return True
            else:
                err_msg += f"status code: {status_code}" 
                
        except requests.ConnectionError:
            err_msg += "Connection Error"
            
        except requests.Timeout:
            err_msg += f"Request Timed Out"
        
        if attempt < retries:
            s = "d"
            for style, msg in {
                f"b;{s}": err_msg,
                f"{s};i;x": ret_msg
            }.items():
                print_error(msg, style)
            
            time.sleep(interval)
            
    abort(err_msg, "p;b")
    
def normalize(text, fallback=None, case="l"):
    if fallback is None and text:
        fallback = text
        
    if not isinstance(text, str):
        return fallback
        
    text = re.sub(r'\s+', ' ', text.strip())
    text = re.sub(r'\s+,', ',', text)
    
    case = str(case).strip()[:1].lower()
    if case == "l":
        return text.lower()
    elif case == "u":
        return text.upper()
    elif case == "p":
        return text.title()
    elif case == "c":
        return text.capitalize()
    else:
        return text
    
def date_to_int(date_str):
    if not isinstance(date_str, str):
        date_str = str(date_str)

    try:
        dts = get_date(date_str=date_str)
        return int(dts)
    except ValueError:
        return 0
        
def new_line(ct=0):
    if not isinstance(ct, int):
        ct = int(ct) if str(ct).isint() else 0
        
    if ct > 0:
        for i in range(1, ct+1):
            print(" ")

def print_msg(code: int, icon: str = "✔", msg: str = "", styles=None):
    cases = []
    for cs in ("proper", "capitalize", "lower", "upper"):
        for n in range(1, 5):
            cases.append(cs[0:n])
    
    cs = cases[0]
    
    color_codes = { "dark": 30, "bright": 90 }
    cd = color_codes["bright"]
    
    fmts = { "b": 1, "d": 2, "i": 3 }
    fmt = ""
    
    breaks = { "prior": 0, "after": 0 }
    
    e = "\033["
    r = f"{e}0m"
    s = " "
    p = 0
    a = 0
    x = 0
    
    if styles:
        if not isinstance(styles, list):
            styles = str(styles) if not isinstance(styles, str) else styles
            styles = styles.split(";") if ";" in styles else [styles]
                
        for style in styles:
            style = normalize(style)
            
            if "case" in ft:
                cs = fv[:1] if fv[:1] in cases else cases[0]
            elif ft in color_codes:
                color_codes[ft] = fv
            elif ft in breaks:
                breaks[ft] = int(fv) if not isinstance(fv, int) else fv
            
            st = normalize(style[:1])
            ct = normalize(style[1:2])
            
            try:
                ct = int(ct) if not isinstance(ct, int) else ct
            except (ValueError, TypeError):
                ct = 1
                
            ct = max(1, min(4, ct))
            
            if st == "s":
                s = " " * ct
            elif st == "p":
                p = ct
            elif st == "a":
                a = ct
            elif st in fmts:
                fmt += f"{formats[st]};"
            elif st == "x":
                x = ct
                          
    icon = icon if x <= 0 else f"{' ' * x}-"
    msg = normalize(msg, case=cs)
    
    try:
        code = int(code)
    except (ValueError, TypeError):
        code = 2
        
    code = max(1, min(code, 7))
    cd = f"{cd+code}m"
    if msg:
        new_line(p)       
        print(f"{e}{fmt.replace('3;', '')}{cd}{s}{icon}{r} {e}{fmt}{cd}{msg}{r}")
        new_line(a)

def print_error(msg: str, styles=None):
    print_msg(1, "✖", msg, styles)

def print_success(msg: str, styles=None):
    print_msg(2, "✔", msg, styles)

def print_warning(msg: str, styles=None):
    print_msg(3, "𝒊", msg, styles)
        
def sort_data(data, sort_key="id"):
    if data:
        return sorted(data, key=lambda x: int(x.get(sort_key, 0)))
    
def resolve_path(path=None, filename=None):
    path = path or os.path.join(os.environ.get('PWD', './'), 'USERDATA')
    
    try:
        os.makedirs(path, exist_ok=True)
    except Exception as e:
        abort(f"Error creating directory '{path}': {e}")
    if filename is not None:
        path = os.path.join(path, filename)
        
    return path

def get_date(date_format="ts", date_str="2022-03-01", expr = "%Y-%m-%d"):
    if date_format == "m":
        return datetime.now().month
        
    elif date_format == "y":
        return datetime.now().year
            
    elif date_format == "mm":
        cy = datetime.now().year
        mos = []
        
        for i in range(1, 13):
            dt = datetime.strptime(f"{cy}-{i:02}-01", expr)
            mo = dt.strftime("%B")
            mos.append(mo)
        
        return tuple(mos)
        
    elif date_format == "ts":
        dt = datetime.strptime(re.split(r"[,\s]+", normalize(date_str))[0], expr)
        return dt.timestamp()
        
    else:
        return 0

def globvar_is_set(var_name, ret=False):
    if var_name in globals() and bool(globals()[var_name]):
        if ret:
            return globals()[var_name]
        else:
            return True
            
    return False
    
def set_global(name=None, value=""):
    name = normalize(name)
    
    if not name:
        print_warning("Error: Variable name should not be empty")
        return
    
    if isinstance(value, str):
        value = normalize(value)
    
    if not globvar_is_set(name):
        globals()[name] = value
        # print_success(f"Name: {name}, Value: {value}")
        
def set_globals(obj=None, value=None):
    if isinstance(obj, str):
        if obj[:1] == "_":
            obj = value
        else:
            if "=" in obj:
                pair = obj.split("=")
                set_global(pair[0], pair[1])
            else:
                set_global(obj, value)
            return
    
    if isinstance(obj, dict):
        for k, v in obj.items():
            set_global(k, v)
    elif isinstance(obj, list):
        for item in obj:
            set_global(item, value)
    else:
        print_warning("Error: Invalid variable type")

def parse_args(args):
    try:
        pairs = shlex.split(args)
        return dict(pair.split('=', 1) for pair in pairs if '=' in pair)
    except ValueError as e:
        print(f"Error parsing arguments: {e}")
        return {}

def clamp(value, level=0, min_val=0.69, max_val=12):
    try:
        value = float(value)
        
        if level == 1:
            max_val = value
            value = value * min_val
        elif level == 2:
            p = 0.1
            max_val = max_val * p
            value = value * min_val * p
            min_val = p
            
        value = max(min_val, min(value, max_val))
    except (TypeError, ValueError):
        value = min_val
    
    return float(value) if level == 2 else int(value)

def init_base_params(args):
    base_timeout = 5
    basic_vars = {
        "sort_key": "timestamp",
        "timeout": clamp(base_timeout),
        "retries": clamp(base_timeout, level=1),
        "sleep": clamp(base_timeout, level=2)
    }
    
    necessary_vars = {
        "homepage": ("hcc", "pgcdc"),
        "username": "login_keys",
        "password": "login_keys",
        "headless": (True, False),
        "verbose": (True, False)
    }
    
    first_item = next(iter(necessary_vars), None)
    params = parse_args(args)
    for var, var_type in necessary_vars.items():
        if isinstance(var_type, str):
            if var not in params:
                abort(f"Variable: [{var}] is necessary")
        params[var] = params.get(var, var_type[0])
    
    homepage_fallback = f"https://{params.get(first_item, None) or necessary_vars.get(first_item, None)[0]}-tams.com.ph"
    params[first_item] = homepage_fallback
    
    for key, value in {
        "_basic_vars": basic_vars,
        "_params": params,
        "login_inputs": tuple(params.keys())[1:3],
        "base_url": f"{homepage_fallback}/tams/",
        "current_month": get_date(date_format="m"),
        "current_year": get_date(date_format="y"),
        "month_strings": get_date(date_format="mm"),
        "url_list": ("attendance", "overtime", "officialbusiness", "leave")
    }.items():
        set_globals(key, value)

def init(args):
    init_base_params(normalize(args))
    
    chrome_options = ["no sandbox", "disable dev shm usage", "disable extensions"]
    if globvar_is_set("headless", True):
        chrome_options.append("headless=new")
        
    options = webdriver.ChromeOptions()
    for opt in chrome_options:
        options.add_argument(f"--{normalize(opt).replace(" ", "-")}")
    
    options.page_load_strategy = "eager"
    options.unhandled_prompt_behavior = "accept"
    options.accept_insecure_certs = True
    
    load_timeout = globvar_is_set("timeout", True) * 1000
    for load_type in ("pageLoad", "implicit", "script"):
        options.timeouts = { load_type: load_timeout }
    
    # Optional: Specify the path to the ChromeDriver if not in PATH
    # DRIVER_PATH = os.getenv("CHROME_DRIVER_PATH", "path/to/chromedriver")
    # driver = webdriver.Chrome(executable_path=DRIVER_PATH, options=options)

    try:
        driver_local = webdriver.Chrome(options=options)
    except WebDriverException as e:
        abort(f"WebDriver error: {e}")
    except Exception as e:
        abort(f"Unexpected error: {e}")
    
    network_cfgs = { "enable": {}, "setBlockedURLs": { "urls": ["*.css"] } }
    for cfg, val in network_cfgs.items():
        driver_local.execute_cdp_cmd(f"Network.{cfg}", val)
        
    set_globals("driver", driver_local)
    if check_internet():
        navigate("Auth")
        driver.save_screenshot("/sdcard/download/ss.png")
        abort()

def abort(msgs=[], styles=None):
    if not isinstance(msgs, list):
        msgs = [str(msgs)]
        
    if globvar_is_set("driver"):
        driver.quit()
    
    if globvar_is_set("verbose", True) and len(msgs) > 0:
        for msg in msgs:
            print_error(msg, styles)
            
    sys.exit(1)
    
    