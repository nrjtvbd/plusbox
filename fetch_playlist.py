import requests
import re
import datetime
import time

CHANNELS = [
    {"id": "BTVWorld", "name": "BTV WORLD"},
    {"id": "GTV", "name": "GAZI TV HD"},
    {"id": "StarJalsha", "name": "STAR JALSHA HD"},
    {"id": "SonyTen1", "name": "SONY TEN 1 HD"}
]

# এখানে ব্যাকআপ ডোমেইনগুলো লিস্ট করা হয়েছে
BACKUP_DOMAINS = [
    "https://backend.plusbox.tv",
    "https://plusbox.tv",
    "http://tv.rangdhanu.live"
]

def get_token(ch_id):
    headers = {
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/147.0.0.0 Safari/537.36",
        "Referer": "https://plusbox.tv/",
        "Accept": "*/*"
    }
    
    for base_url in BACKUP_DOMAINS:
        try:
            # ব্যাকআপ সার্ভার থেকে টোকেন খোঁজা
            url = f"{base_url}/{ch_id}/embed.html"
            if "play.php" not in url:
                # সরাসরি এম্বেড পেজ ট্রাই করা
                response = requests.get(url, headers=headers, timeout=10)
                token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
                
                if token_match:
                    print(f"✅ Token found using backup: {base_url}")
                    return token_match.group(1)
        except:
            continue
            
    return None

def main():
    entries = []
    print("🚀 Attempting Plusbox Fetch with Backup Servers...")
    
    for ch in CHANNELS:
        token = get_token(ch['id'])
        if token:
            # ব্যাকআপ সার্ভারের লিঙ্ক ফরম্যাট
            stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
            entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ {ch['name']} Success")
        else:
            print(f"❌ {ch['name']} Failed")
        time.sleep(2)

    with open("playlist.m3u", "w") as f:
        f.write("#EXTM3U\n# Backup Update: " + str(datetime.datetime.now()) + "\n" + "\n".join(entries))
    print("🎉 Sync Complete!")

if __name__ == "__main__":
    main()
