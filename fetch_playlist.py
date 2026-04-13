import re
import time
import datetime
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options

# --- Configuration ---
BASE_URL = "https://backend.plusbox.tv/"
PLAYLIST_FILENAME = "playlist.m3u"
MAX_WORKERS = 1  # আইপি ব্লক এড়াতে একের পর এক রিকোয়েস্ট পাঠানো ভালো

CHANNELS = [
    {"id": "TSportsHD", "name": "T-SPORTS HD", "group": "Sports"},
    {"id": "BTVWorld", "name": "BTV WORLD", "group": "Entertainment"},
    {"id": "GaziTVHD", "name": "GAZI TV HD", "group": "Entertainment"},
    {"id": "StarJalshaHD", "name": "STAR JALSHA HD", "group": "Entertainment"},
    {"id": "SonyTen1HD", "name": "SONY TEN 1 HD", "group": "Sports"}
]

def get_plusbox_stream(channel_info):
    ch_id, ch_name, ch_group = channel_info
    driver = None
    try:
        chrome_options = Options()
        chrome_options.add_argument("--headless")
        chrome_options.add_argument("--no-sandbox")
        chrome_options.add_argument("--disable-dev-shm-usage")
        chrome_options.add_argument("--window-size=1920,1080")
        # অটোমেশন ডিটেকশন এড়ানোর জন্য ফ্ল্যাগ
        chrome_options.add_experimental_option("excludeSwitches", ["enable-automation"])
        chrome_options.add_experimental_option('useAutomationExtension', False)
        
        driver = webdriver.Chrome(options=chrome_options)
        
        # সেশন তৈরির জন্য প্রথমে মেইন সাইটে যাওয়া
        driver.get("https://plusbox.tv/")
        time.sleep(3)

        player_url = f"{BASE_URL}{ch_id}/embed.html"
        print(f"📡 Fetching: {ch_name}...")
        driver.get(player_url)
        
        # সোর্স লোড হওয়া পর্যন্ত কয়েকবার চেক করা
        token = None
        for _ in range(3): # ৩ বার চেষ্টা করবে
            time.sleep(5)
            page_source = driver.page_source
            token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', page_source)
            if token_match:
                token = token_match.group(1)
                break
        
        if token:
            stream_url = f"{BASE_URL}{ch_id}/index.fmp4.m3u8?token={token}"
            print(f"✅ Success: {ch_name}")
            return f'#EXTINF:-1 tvg-name="{ch_name}" group-title="{ch_group}",{ch_name}\n{stream_url}'
        
        return None
    except Exception:
        return None
    finally:
        if driver: driver.quit()

def main():
    channels_to_process = [(ch['id'], ch['name'], ch['group']) for ch in CHANNELS]
    print(f"🚀 Starting Stealth Fetch for {len(channels_to_process)} channels...")

    # একের পর এক (Sequential) কাজ করলে ব্লক হওয়ার ভয় কম থাকে
    playlist_entries = []
    for ch in channels_to_process:
        result = get_plusbox_stream(ch)
        if result:
            playlist_entries.append(result)
        time.sleep(2) # গ্যাপ রাখা হচ্ছে

    if playlist_entries:
        updated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        final_content = ['#EXTM3U', f'# Last Updated: {updated_at}'] + playlist_entries
        with open(PLAYLIST_FILENAME, "w") as f:
            f.write("\n".join(final_content))
        print(f"✅ Playlist updated with {len(playlist_entries)} channels!")
    else:
        print("🛑 All attempts failed. Plusbox is blocking GitHub data centers.")

if __name__ == "__main__":
    main()
