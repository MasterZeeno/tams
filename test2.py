import requests
from bs4 import BeautifulSoup
from datetime import datetime, timedelta
import json
import os

USER_AGENT_FILE = "user_agents.json"

# List of sources with a handler function
SOURCES = [
    {
        "name": "WhatIsMyBrowser",
        "url": "https://developers.whatismybrowser.com/useragents/explore/software_name/chrome/",
        "handler": "parse_whatsmybrowser"
    },
    {
        "name": "UserAgentString.com",
        "url": "http://www.useragentstring.com/pages/useragentstring.php?name=Chrome",
        "handler": "parse_useragentstring"
    },
    {
        "name": "DeviceAtlas",
        "url": "https://deviceatlas.com/blog/list-of-user-agent-strings",
        "handler": "parse_deviceatlas"
    }
]

def parse_whatsmybrowser(html):
    soup = BeautifulSoup(html, "html.parser")
    return [a.text.strip() for a in soup.select("td.useragent a") if "Mobile" not in a.text]

def parse_useragentstring(html):
    soup = BeautifulSoup(html, "html.parser")
    return [li.text.strip() for li in soup.select("ul li") if "Mobile" not in li.text]

def parse_deviceatlas(html):
    soup = BeautifulSoup(html, "html.parser")
    return [code.text.strip() for code in soup.select("code") if "Chrome" in code.text and "Mobile" not in code.text]
    
def fetch_user_agents():
    for source in SOURCES:
        try:
            print(f"Trying {source['name']}...")
            res = requests.get(source['url'], timeout=10, headers={
                "User-Agent": "Mozilla/5.0"
            })
            res.raise_for_status()

            handler = globals()[source["handler"]]
            user_agents = handler(res.text)
            if user_agents:
                return user_agents
        except Exception as e:
            print(f"Failed: {source['name']} — {e}")
    return []

def save_user_agents(user_agents):
    today = datetime.now().strftime("%Y-%m-%d")

    if os.path.exists(USER_AGENT_FILE):
        with open(USER_AGENT_FILE, "r") as f:
            data = json.load(f)
    else:
        data = {}

    last_date = max(data.keys(), default="2000-01-01")
    last_updated = datetime.strptime(last_date, "%Y-%m-%d")
    if datetime.now() - last_updated < timedelta(days=7):
        print("User-agent file is still fresh.")
        return

    if today in data and data[today] == user_agents:
        print("User-agent data has not changed. Skipping update.")
        return

    data[today] = user_agents
    with open(USER_AGENT_FILE, "w") as f:
        json.dump(data, f, indent=2)
    print(f"Saved {len(user_agents)} user agents for {today}.")
    
if __name__ == "__main__":
    user_agents = fetch_user_agents()
    if user_agents:
        save_user_agents(user_agents)
    else:
        print("Failed to fetch user-agents from all sources.")