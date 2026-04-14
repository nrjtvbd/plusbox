import requests
import cloudscraper
import re
import datetime

# --- Configuration ---
PLAYLIST_FILENAME = "playlist.m3u"
CHANNELS = [
    {"id": "525", "name": "BTV WORLD"},
    {"id": "531", "name": "GAZI TV HD"},
    {"id": "540", "name": "STAR JALSHA HD"},
    {"id": "580", "name": "SONY TEN 1 HD"}
]

def get_token(ch_id):
    scraper = cloudscraper.create_scraper()
    headers = {
        "Referer": "https://plusbox.tv/",
        "User-Agent": "Mozilla/5.0 (Linux; Android 10; K) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Mobile Safari/537.36"
    }
    try:
        url = f"https://plusbox.tv/play.php?id={ch_id}"
        response = scraper.get(url, headers=headers, timeout=15)
        # টোকেন খোঁজার রিজেক্স
        token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        if token_match:
            return token_match.group(1)
    except Exception as e:
        print(f"Error for ID {ch_id}: {e}")
    return None

def main():
    print("🚀 Starting Plusbox Direct Fetcher (Termux)...")
    playlist_entries = []
    
    for ch in CHANNELS:
        print(f"📡 Requesting: {ch['name']}...")
        token = get_token(ch['id'])
        if token:
            stream_url = f"https://plusbox.tv/live/{ch['id']}/index.m3u8?token={token}"
            playlist_entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
            print("✅ Success!")
        else:
            print("❌ Failed to get token.")

    header = f"#EXTM3U\n# Last Updated: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M')}\n"
    with open(PLAYLIST_FILENAME, "w") as f:
        f.write(header + "\n".join(playlist_entries))
    
    print(f"\n🎉 Process Complete! {len(playlist_entries)} channels saved.")

if __name__ == "__main__":
    main()
