import requests
from bs4 import BeautifulSoup
import json
from pathlib import Path
from datetime import datetime, timedelta

def get_latest_user_agents_json(save_path: str = "user_agents.json"):
    today = datetime.today().strftime("%Y-%m-%d")
    save_file = Path(save_path)
    existing_data = {}

    if save_file.exists():
        with open(save_file, "r", encoding="utf-8") as f:
            try:
                existing_data = json.load(f)
            except json.JSONDecodeError:
                pass  # Corrupted or empty file

        # Check last updated date
        if existing_data:
            last_updated = max(existing_data.keys())
            days_since = (datetime.today() - datetime.strptime(last_updated, "%Y-%m-%d")).days
            if days_since < 7:
                return f"No update needed. Last updated {days_since} day(s) ago."

    # Scrape HasData user agents
    url = "https://hasdata.com/blog/user-agents-for-web-scraping"
    response = requests.get(url)
    response.raise_for_status()

    soup = BeautifulSoup(response.text, "html.parser")
    user_agents = sorted({code.get_text(strip=True)
                          for code in soup.find_all("code")
                          if code.get_text(strip=True).startswith("Mozilla/")})

    # Skip if data is the same
    if existing_data:
        latest_agents = existing_data.get(last_updated, [])
        if sorted(latest_agents) == user_agents:
            return "No update needed. User-agent list is unchanged."

    # Update and save
    existing_data[today] = user_agents
    save_file.parent.mkdir(parents=True, exist_ok=True)
    with open(save_file, "w", encoding="utf-8") as f:
        json.dump(existing_data, f, indent=2, ensure_ascii=False)

    return f"Updated user agents on {today} and saved to {save_path}."