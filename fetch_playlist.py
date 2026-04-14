import requests
import cloudscraper
import re
import datetime
import time

CHANNELS = [
    {"id": "BTVWorld", "name": "BTV World"},
    {"id": "ATNBangla", "name": "ATN Bangla"},
    {"id": "TSportsHD", "name": "T Sports HD"},
    {"id": "SomoyTv", "name": "Somoy TV"},
    {"id": "GaziTVHD", "name": "Gazi TV HD"}
]

def get_token(ch_id):
    # সেশন হ্যান্ডলার
    session = requests.Session()
    scraper = cloudscraper.create_scraper(sess=session)
    
    # এটি গিটহাবের আইপি লুকানোর জন্য মোবাইল হেডার
    headers = {
        "User-Agent": "Mozilla/5.0 (Linux; Android 13; SM-S918B) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/116.0.0.0 Mobile Safari/537.36",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8",
        "Accept-Language": "en-US,en;q=0.5",
        "Referer": "https://plusbox.tv/",
        "X-Requested-With": "com.android.chrome",
        "Sec-Fetch-Mode": "navigate",
        "Connection": "keep-alive"
    }

    try:
        # আমরা সরাসরি backend.plusbox.tv এর পরিবর্তে plusbox.tv/play.php কে হিট করছি
        # কারণ মেইন ডোমেইনে ব্লক কিছুটা কম থাকে
        url = f"https://plusbox.tv/play.php?id={ch_id}"
        response = scraper.get(url, headers=headers, timeout=20)
        
        # সোর্স কোডে টোকেন খোঁজা
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        
        if token_match:
            return token_match.group(1)
            
    except Exception as e:
        print(f"Error: {e}")
    return None

def main():
    print("🚀 Running Mobile-Masking Auto Fetcher...")
    entries = []
    
    for ch in CHANNELS:
        print(f"📡 Requesting: {ch['name']}...")
        token = get_token(ch['id'])
        if token:
            stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
            entries.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print("✅ Success!")
        else:
            print("❌ Blocked by Server.")
        time.sleep(5) # ৫ সেকেন্ড বিরতি যাতে সার্ভার সন্দেহ না করে

    with open("playlist.m3u", "w") as f:
        f.write("#EXTM3U\n# Sync: " + str(datetime.datetime.now()) + "\n" + "\n".join(entries))
    print("🎉 Finish!")

if __name__ == "__main__":
    main()
