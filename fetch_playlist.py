import requests
import cloudscraper
import re
import datetime
import time

# চ্যানেলের আইডিগুলো আপনার পাঠানো লগ অনুযায়ী আপডেট করা হয়েছে
CHANNELS = [
    {"id": "BTVWorld", "name": "BTV World"},
    {"id": "ATNBangla", "name": "ATN Bangla"},
    {"id": "TSportsHD", "name": "T Sports HD"},
    {"id": "GTV", "name": "Gazi TV"},
    {"id": "StarJalsha", "name": "Star Jalsha"}
]

def get_token(ch_id):
    # ক্লাউডস্ক্র্যাপার ব্যবহার করে ব্রাউজার ইমুলেশন
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # আপনার পাঠানো লগের একদম হুবহু হেডার
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Accept": "*/*",
        "Referer": f"https://backend.plusbox.tv/{ch_id}/embed.html",
        "Origin": "https://backend.plusbox.tv",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty",
        "Accept-Language": "en-US,en;q=0.9"
    }

    try:
        # সরাসরি ব্যাকএন্ড এম্বেড ইউআরএল থেকে টোকেন খোঁজা
        embed_url = f"https://backend.plusbox.tv/{ch_id}/embed.html"
        response = scraper.get(embed_url, headers=headers, timeout=20)
        
        # রিজেক্স দিয়ে টোকেন এক্সট্রাক্ট করা
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        
        if token_match:
            return token_match.group(1)
        else:
            # যদি এম্বেড পেজে না পাওয়া যায়, তবে প্লাসবক্সের মেইন প্লে পেজে ট্রাই করবে
            alt_url = f"https://plusbox.tv/play.php?id={ch_id}"
            alt_response = scraper.get(alt_url, headers=headers, timeout=20)
            alt_token = re.search(r'token=([a-zA-Z0-9\-_.]+)', alt_response.text)
            if alt_token:
                return alt_token.group(1)
                
    except Exception as e:
        print(f"⚠️ Error for {ch_id}: {e}")
    
    return None

def main():
    print("🚀 Starting Multi-Channel Auto Token Generator...")
    entries = []
    
    for ch in CHANNELS:
        print(f"📡 Fetching Token for: {ch['name']}...")
        token = get_token(ch['id'])
        
        if token:
            # fmp4 ফরম্যাট ব্যবহার করা হয়েছে যা আপনার পাঠানো লগে ছিল
            stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
            entries.append(f'#EXTINF:-1 tvg-id="{ch["id"]}" tvg-name="{ch["name"]}" tvg-logo="http://tv.rangdhanu.live/img/rangdhanulive.png",{ch["name"]}\n{stream_url}')
            print(f"✅ Success!")
        else:
            print(f"❌ Failed to get token.")
        
        # সার্ভার যাতে ব্লক না করে তাই সামান্য বিরতি
        time.sleep(3)

    # প্লেলিস্ট ফাইল তৈরি
    header = f"#EXTM3U\n# Auto Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n"
    with open("playlist.m3u", "w") as f:
        f.write(header + "\n".join(entries))
    
    print("\n🎉 Process finished. Check your playlist.m3u file.")

if __name__ == "__main__":
    main()
