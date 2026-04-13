import re
import time
import datetime
import cloudscraper
import requests

# --- Configuration ---
BASE_URL = "https://backend.plusbox.tv/"
PLAYLIST_FILENAME = "playlist.m3u"

CHANNELS = [
    {"id": "TSportsHD", "name": "T-SPORTS HD", "group": "Sports"},
    {"id": "BTVWorld", "name": "BTV WORLD", "group": "Entertainment"},
    {"id": "GaziTVHD", "name": "GAZI TV HD", "group": "Entertainment"},
    {"id": "StarJalshaHD", "name": "STAR JALSHA HD", "group": "Entertainment"},
    {"id": "SonyTen1HD", "name": "SONY TEN 1 HD", "group": "Sports"}
]

def get_token_stealth(ch_id):
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    url = f"{BASE_URL}{ch_id}/embed.html"
    headers = {
        "Referer": "https://plusbox.tv/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    try:
        # সেশন সতেজ রাখতে প্রথমে মেইন সাইট একবার ভিজিট
        scraper.get("https://plusbox.tv/", timeout=10)
        time.sleep(2)
        
        response = scraper.get(url, headers=headers, timeout=15)
        html = response.text
        
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', html)
        if token_match:
            return token_match.group(1)
        
        # যদি প্রথমবার না পায়, তবে স্ক্রিপ্ট সোর্স থেকে খোঁজার চেষ্টা
        js_match = re.search(r'["\']?token["\']?\s*[:=]\s*["\']([^"\']+)["\']', html)
        return js_match.group(1) if js_match else None
    except Exception as e:
        print(f"Connection error for {ch_id}: {e}")
        return None

def main():
    print(f"🚀 Starting Hybrid Stealth Fetch...")
    playlist_entries = []
    
    for ch in CHANNELS:
        print(f"📡 Requesting: {ch['name']}...")
        token = get_token_stealth(ch['id'])
        
        if token:
            stream_url = f"{BASE_URL}{ch['id']}/index.fmp4.m3u8?token={token}"
            playlist_entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="{ch["group"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ Success!")
        else:
            print(f"❌ Failed to get token.")
        time.sleep(3) # আইপি ব্লক এড়াতে বিরতি

    if playlist_entries:
        updated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        content = ["#EXTM3U", f"# Last Updated: {updated_at}"] + playlist_entries
        with open(PLAYLIST_FILENAME, "w") as f:
            f.write("\n".join(content))
        print(f"🎉 Playlist updated with {len(playlist_entries)} channels!")
    else:
        print("🛑 All methods failed. Plusbox is currently impenetrable from GitHub.")

if __name__ == "__main__":
    main()
