import os
import sys
import json
import re
from datetime import datetime, timedelta, timezone
import requests
from bs4 import BeautifulSoup

def fetch_contributions(username: str) -> dict:
    """
    Scrapes the GitHub public contribution calendar for the given user.
    Calculates total contributions, current streak, and longest streak.
    """
    url = f"https://github.com/users/{username}/contributions"
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, Gecko) Chrome/120.0.0.0 Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8"
    }
    
    print(f"Fetching contribution data for user '{username}' from {url}...")
    resp = requests.get(url, headers=headers)
    if resp.status_code != 200:
        print(f"Warning: HTTP {resp.status_code} received when fetching contributions.")
        # Fallback request to main profile page
        url = f"https://github.com/{username}"
        resp = requests.get(url, headers=headers)
        if resp.status_code != 200:
            raise Exception(f"Failed to fetch profile page for {username}, HTTP {resp.status_code}")

    soup = BeautifulSoup(resp.text, "html.parser")
    
    # Extract tooltips for count lookup if needed
    tooltips = {}
    for tt in soup.find_all("tool-tip"):
        for_id = tt.get("for")
        if for_id:
            text = tt.get_text(strip=True)
            # Example text: "No contributions on January 15, 2025" or "5 contributions on January 16, 2025"
            match = re.search(r"(\d+|No)\s+contributions?\s+on\s+([A-Za-z]+\s+\d+,\s+\d{4})", text)
            if match:
                count_str = match.group(1)
                count = 0 if count_str == "No" else int(count_str)
                tooltips[for_id] = count

    days = []
    # Find all calendar day elements (td or rect with data-date)
    day_elements = soup.find_all(attrs={"data-date": True})
    
    if not day_elements:
        print("No data-date elements found directly. Attempting pattern matching on calendar grid...")

    for el in day_elements:
        date_str = el.get("data-date")
        if not date_str:
            continue
            
        el_id = el.get("id")
        level_str = el.get("data-level", "0")
        try:
            level = int(level_str)
        except ValueError:
            level = 0
            
        count = None
        if el.get("data-count") is not None:
            try:
                count = int(el.get("data-count"))
            except ValueError:
                pass
                
        if count is None and el_id in tooltips:
            count = tooltips[el_id]
            
        if count is None:
            # Fallback estimation from level if count unavailable
            level_estimates = {0: 0, 1: 2, 2: 5, 3: 10, 4: 15}
            count = level_estimates.get(level, 0)
            
        days.append({
            "date": date_str,
            "count": count,
            "level": level
        })

    # Sort days chronologically
    days.sort(key=lambda x: x["date"])
    
    # Calculate Streaks & Summary
    total_contributions = sum(d["count"] for d in days)
    
    current_streak = 0
    longest_streak = 0
    temp_streak = 0
    
    now_utc = datetime.now(timezone.utc)
    today_str = now_utc.strftime("%Y-%m-%d")
    yesterday_str = (now_utc - timedelta(days=1)).strftime("%Y-%m-%d")
    
    for d in days:
        if d["count"] > 0:
            temp_streak += 1
            if temp_streak > longest_streak:
                longest_streak = temp_streak
        else:
            temp_streak = 0

    # Calculate active current streak leading up to today or yesterday
    active_streak = 0
    for d in reversed(days):
        if d["count"] > 0:
            active_streak += 1
        else:
            # If today has 0 contributions yet, allow yesterday to maintain the streak
            if d["date"] == today_str:
                continue
            else:
                break
                
    current_streak = active_streak

    data = {
        "username": username,
        "updated_at": now_utc.isoformat(),
        "total_contributions": total_contributions,
        "current_streak": current_streak,
        "longest_streak": longest_streak,
        "days": days
    }
    
    return data

def main():
    username = os.getenv("GH_PROFILE_USER", "Divyanshu-Jaiswal-17")
    repo_root = os.path.abspath(os.path.join(os.path.dirname(__file__), ".."))
    data_dir = os.path.join(repo_root, "data")
    output_path = os.path.join(data_dir, "contributions.json")
    
    os.makedirs(data_dir, exist_ok=True)
    
    try:
        contrib_data = fetch_contributions(username)
        with open(output_path, "w", encoding="utf-8") as f:
            json.dump(contrib_data, f, indent=2)
        print(f"Successfully scraped {len(contrib_data['days'])} days of contributions for '{username}'.")
        print(f"Total: {contrib_data['total_contributions']}, Current Streak: {contrib_data['current_streak']}, Longest Streak: {contrib_data['longest_streak']}")
        print(f"Saved data to: {output_path}")
    except Exception as e:
        print(f"Error fetching contributions: {e}")
        # Write dummy fallback data if fetch fails
        if not os.path.exists(output_path):
            fallback_days = []
            today = datetime.utcnow()
            for i in range(365, -1, -1):
                d = today - timedelta(days=i)
                fallback_days.append({
                    "date": d.strftime("%Y-%m-%d"),
                    "count": 0,
                    "level": 0
                })
            fallback_data = {
                "username": username,
                "updated_at": datetime.utcnow().isoformat() + "Z",
                "total_contributions": 0,
                "current_streak": 0,
                "longest_streak": 0,
                "days": fallback_days
            }
            with open(output_path, "w", encoding="utf-8") as f:
                json.dump(fallback_data, f, indent=2)
            print(f"Fallback contributions saved to: {output_path}")
        sys.exit(1)

if __name__ == "__main__":
    main()
