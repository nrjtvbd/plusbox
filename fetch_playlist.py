import requests
import cloudscraper
import re
import datetime
import time

CHANNELS = [
    {"id": "BTVWorld", "name": "BTV WORLD"},
    {"id": "GTV", "name": "GAZI TV HD"},
    {"id": "StarJalsha", "name": "STAR JALSHA HD"},
    {"id": "SonyTen1", "name": "SONY TEN 1 HD"}
]

def get_token(ch_id):
    # সেশন এবং স্ক্র্যাপার সেটআপ
    scraper = cloudscraper.create_scraper(
        browser={
            'browser': 'chrome',
            'platform': 'windows',
            'desktop': True
        }
    )
    
    # আপনার পাঠানো লগ অনুযায়ী হেডার সেট করা হয়েছে
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Referer": f"https://backend.plusbox.tv/{ch_id}/embed.html",
        "Origin": "https://backend.plusbox.tv",
        "Accept": "*/*",
        "Sec-Fetch-Site": "same-origin",
        "Sec-Fetch-Mode": "cors",
        "Sec-Fetch-Dest": "empty"
    }

    try:
        # সরাসরি ব্যাকএন্ড থেকে টোকেন নেয়ার চেষ্টা
        url = f"https://backend.plusbox.tv/{ch_id}/embed.html"
        response = scraper.get(url, headers=headers, timeout=20)
        
        # আপনার লগের টোকেন ফরম্যাট অনুযায়ী রিজেক্স (Regex)
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        
        if not token_match:
            # যদি এম্বেড পেজে না পাওয়া যায়, তবে মেইন সাইটে ট্রাই করবে
            main_url = f"https://plusbox.tv/play.php?id={ch_id}"
            response = scraper.get(main_url, headers=headers, timeout=20)
            token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)

        if token_match:
            return token_match.group(1)
            
    except Exception as e:
        print(f"Error fetching {ch_id}: {e}")
    return None

def main():
    entries = []
    print("🚀 Starting Plusbox Dynamic Fetcher...")
    
    for ch in CHANNELS:
        token = get_token(ch['id'])
        if token:
            # নতুন ইউআরএল ফরম্যাট: backend.plusbox.tv ব্যবহার করা হয়েছে
            stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
            entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" tvg-logo="http://tv.rangdhanu.live/img/rangdhanulive.png",{ch["name"]}\n{stream_url}')
            print(f"✅ {ch['name']} Success")
        else:
            print(f"❌ {ch['name']} Failed")
        time.sleep(3)

    with open("playlist.m3u", "w") as f:
        f.write("#EXTM3U\n# Updated: " + str(datetime.datetime.now()) + "\n" + "\n".join(entries))
    print("🎉 Playlist Updated Successfully!")

if __name__ == "__main__":
    main()
