import re
import time
import datetime
import concurrent.futures
from selenium import webdriver
from selenium.webdriver.chrome.options import Options
from selenium.webdriver.chrome.service import Service
from webdriver_manager.chrome import ChromeDriverManager

# --- Configuration ---
BASE_URL = "https://backend.plusbox.tv/"
PLAYLIST_FILENAME = "plusbox_playlist.m3u"
MAX_WORKERS = 3  # প্লাসবক্সের জন্য ওয়ার্কার কম রাখা ভালো যাতে আইপি ব্লক না হয়

# প্লাসবক্স চ্যানেল লিস্ট
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
        # আসল ব্রাউজারের মতো আচরণ করার জন্য হেডার
        chrome_options.add_argument("user-agent=Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36")
        
        driver = webdriver.Chrome(service=Service(ChromeDriverManager().install()), options=chrome_options)
        
        # এমবেড পেজে সরাসরি হিট করা
        player_url = f"{BASE_URL}{ch_id}/embed.html"
        driver.get(player_url)
        time.sleep(10)  # জাভাস্ক্রিপ্ট লোড হওয়ার জন্য পর্যাপ্ত সময়

        page_source = driver.page_source
        # টোকেন খুঁজে বের করার লজিক
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', page_source)
        
        if token_match:
            token = token_match.group(1)
            stream_url = f"{BASE_URL}{ch_id}/index.fmp4.m3u8?token={token}"
            print(f"✅ Extracted: {ch_name}")
            return f'#EXTINF:-1 tvg-name="{ch_name}" group-title="{ch_group}",{ch_name}\n{stream_url}'
        
        return None
    except Exception as e:
        print(f"❌ Error on {ch_name}: {e}")
        return None
    finally:
        if driver:
            driver.quit()

def main():
    start_time = time.time()
    channels_to_process = [(ch['id'], ch['name'], ch['group']) for ch in CHANNELS]
    
    print(f"🚀 Starting Plusbox fetcher for {len(channels_to_process)} channels...")

    with concurrent.futures.ThreadPoolExecutor(max_workers=MAX_WORKERS) as executor:
        results = list(executor.map(get_plusbox_stream, channels_to_process))
        playlist_entries = [res for res in results if res is not None]

    if playlist_entries:
        updated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        final_content = ['#EXTM3U', f'# Last Updated: {updated_at}'] + playlist_entries
        with open(PLAYLIST_FILENAME, "w") as f:
            f.write("\n".join(final_content))
        print(f"✅ Playlist created with {len(playlist_entries)} channels!")
    else:
        print("🛑 Failed to extract any tokens.")

if __name__ == "__main__":
    main()
