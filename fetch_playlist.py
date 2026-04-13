import re
import time
import datetime
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

def get_token_via_proxy(ch_id):
    # ফ্রি প্রক্সি লিস্ট (এগুলো কাজ না করলে বাংলাদেশের কোনো প্রক্সি ইউআরএল এখানে দেওয়া যায়)
    proxies_list = [
        None, # প্রথমে প্রক্সি ছাড়া চেষ্টা
        "http://45.72.55.122:8080", 
        "http://185.162.229.155:80"
    ]
    
    url = f"{BASE_URL}{ch_id}/embed.html"
    headers = {
        "Referer": "https://plusbox.tv/",
        "User-Agent": "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36"
    }

    for proxy_url in proxies_list:
        proxies = {"http": proxy_url, "https": proxy_url} if proxy_url else None
        try:
            print(f"Trying {'Proxy: ' + proxy_url if proxy_url else 'Direct Connection'}...")
            response = requests.get(url, headers=headers, proxies=proxies, timeout=10)
            if response.status_code == 200:
                html = response.text
                token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', html)
                if token_match:
                    return token_match.group(1)
        except:
            continue
    return None

def main():
    print(f"🚀 Starting Emergency Proxy Fetch...")
    playlist_entries = []
    
    for ch in CHANNELS:
        print(f"📡 Requesting: {ch['name']}...")
        token = get_token_via_proxy(ch['id'])
        
        if token:
            stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
            playlist_entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}" group-title="{ch["group"]}",{ch["name"]}\n{stream_url}')
            print(f"✅ Success!")
        else:
            print(f"❌ Failed to get token.")
        time.sleep(2)

    if playlist_entries:
        updated_at = datetime.datetime.utcnow().strftime("%Y-%m-%d %H:%M UTC")
        content = ["#EXTM3U", f"# Last Updated: {updated_at}"] + playlist_entries
        with open(PLAYLIST_FILENAME, "w") as f:
            f.write("\n".join(content))
        print(f"🎉 Playlist updated with {len(playlist_entries)} channels!")
    else:
        print("🛑 All attempts failed. Plusbox is extremely secured against Cloud IPs.")

if __name__ == "__main__":
    main()
