import requests
import cloudscraper
import re
import datetime
import time

CHANNELS = [
    {"id": "525", "name": "BTV WORLD"},
    {"id": "531", "name": "GAZI TV HD"},
    {"id": "540", "name": "STAR JALSHA HD"},
    {"id": "580", "name": "SONY TEN 1 HD"}
]

def get_token(ch_id):
    # সেশন তৈরি করে ব্রাউজার ইমুলেট করা
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    headers = {
        "Referer": "https://plusbox.tv/",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/webp,*/*;q=0.8",
        "Upgrade-Insecure-Requests": "1"
    }

    try:
        # প্লাসবক্স এখন সরাসরি লিঙ্ক ব্লক করলে আমরা রিডাইরেক্ট মেথড ট্রাই করছি
        response = scraper.get(f"https://plusbox.tv/play.php?id={ch_id}", headers=headers, timeout=20)
        
        # সোর্স কোডে টোকেন খোঁজা
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        if token_match:
            return token_match.group(1)
            
    except Exception:
        pass
    return None

def main():
    entries = []
    for ch in CHANNELS:
        token = get_token(ch['id'])
        if token:
            url = f"https://plusbox.tv/live/{ch['id']}/index.m3u8?token={token}"
            entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}",{ch["name"]}\n{url}')
            print(f"✅ {ch['name']} Success")
        else:
            print(f"❌ {ch['name']} Failed")
        time.sleep(2)

    with open("playlist.m3u", "w") as f:
        f.write("#EXTM3U\n" + "\n".join(entries))

if __name__ == "__main__":
    main()
