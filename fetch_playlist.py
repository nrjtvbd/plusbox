import requests
import cloudscraper
import re
import datetime
import time

# আপনার পাঠানো HTML সোর্স থেকে নেওয়া চ্যানেলের তালিকা
CHANNELS = [
    {"id": "BTVWorld", "name": "BTV World"},
    {"id": "ATNBangla", "name": "ATN Bangla"},
    {"id": "ATNNews", "name": "ATN News"},
    {"id": "TSportsHD", "name": "T Sports HD"},
    {"id": "TSports", "name": "T Sports"},
    {"id": "SomoyTv", "name": "Somoy TV"},
    {"id": "GaziTVHD", "name": "Gazi TV HD"},
    {"id": "JamunaTV", "name": "Jamuna TV"},
    {"id": "RTV", "name": "RTV"},
    {"id": "Channel24", "name": "Channel 24"}
]

def get_token(ch_id):
    # সেশন এবং ব্রাউজার সেটআপ
    scraper = cloudscraper.create_scraper(
        browser={'browser': 'chrome', 'platform': 'windows', 'desktop': True}
    )
    
    # প্লাসবক্সের সিকিউরিটি বাইপাস করার জন্য সবচেয়ে শক্তিশালী হেডার
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36",
        "Referer": "https://plusbox.tv/",
        "Origin": "https://plusbox.tv",
        "Accept": "text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8",
        "Sec-Fetch-Site": "same-site",
        "Sec-Fetch-Mode": "navigate",
        "Sec-Fetch-Dest": "iframe"
    }

    try:
        # আমরা সরাসরি এম্বেড পেজের সোর্স কোড থেকে টোকেনটি টানবো
        # প্লাসবক্স এই পেজেই টোকেনটি প্রিন্ট করে রাখে
        url = f"https://backend.plusbox.tv/{ch_id}/embed.html"
        response = scraper.get(url, headers=headers, timeout=15)
        
        # টোকেন খোঁজার রিজেক্স (Regex)
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        
        if token_match:
            return token_match.group(1)
        
        # বিকল্প পথ: যদি এম্বেড পেজে না পাওয়া যায়
        alt_url = f"https://plusbox.tv/play.php?id={ch_id}"
        alt_response = scraper.get(alt_url, headers=headers, timeout=15)
        alt_token = re.search(r'token=([a-zA-Z0-9\-_.]+)', alt_response.text)
        if alt_token:
            return alt_token.group(1)

    except Exception as e:
        print(f"⚠️ Error for {ch_id}: {e}")
    return None

def main():
    print("🚀 Running Plusbox Auto-Generator (No-Hassle Mode)...")
    entries = []
    
    for ch in CHANNELS:
        print(f"📡 Fetching: {ch['name']}...")
        token = get_token(ch['id'])
        
        if token:
            # সঠিক স্ট্রিম ইউআরএল তৈরি
            stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
            entries.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ Success!")
        else:
            print(f"❌ Failed.")
        
        time.sleep(2) # ২ সেকেন্ড বিরতি

    # মেইন প্লেলিস্ট ফাইল রাইট করা
    with open("playlist.m3u", "w") as f:
        f.write("#EXTM3U\n# Auto Updated: " + str(datetime.datetime.now()) + "\n" + "\n".join(entries))
    
    print("\n🎉 All Done! Playlist updated.")

if __name__ == "__main__":
    main()
