import requests
import sys
import time
from prompter import print_success, print_error, print_warning

def check_internet(url='https://www.google.com', timeout=10, retries=3):
    for attempt in range(1, retries + 1):
        try:
            response = requests.get(url, timeout=timeout)
            if response.status_code == 200:
                print_success("Internet connection verified.")
                return True
            else:
                print_error(f"Received unexpected status code: {response.status_code}")
        except requests.ConnectionError as e:
            print_error(f"Attempt {attempt}/{retries} failed: Connection error: {e}")
        except requests.Timeout:
            print_error(f"Attempt {attempt}/{retries} failed: Request timed out.")
        
        if attempt < retries:
            print_warning("Retrying in 1 second...")
            time.sleep(1)
    print_error("Failed to establish internet connection after multiple attempts.")
    sys.exit(1)