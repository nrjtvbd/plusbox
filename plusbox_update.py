import requests
import re
import base64
import os

# গিটহাব থেকে সিক্রেট হিসেবে টোকেনটি নেওয়া হবে
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox" 
FILE_PATH = "plusbox.m3u8"

def get_plusbox_token():
    # বিটিভি ওয়ার্ল্ড এর এমবেড লিঙ্ক
    url = "https://backend.plusbox.tv/BTVWorld/embed.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/120.0.0.0 Safari/537.36',
        'Referer': 'https://plusbox.tv/',
        'Origin': 'https://plusbox.tv',
        'Accept-Language': 'en-US,en;q=0.9'
    }
    try:
        response = requests.get(url, headers=headers, timeout=20)
        # যদি রেসপন্স কোড ২০০ হয় তবেই টোকেন খুঁজবো
        if response.status_code == 200:
            match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
            if match:
                return match.group(1)
        print(f"Server Response Code: {response.status_code}")
        return None
    except Exception as e:
        print(f"Error: {e}")
        return None

def generate_playlist(token):
    channels = [
        {"name": "T-SPORTS HD", "id": "TSportsHD"},
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "GAZI TV HD", "id": "GaziTVHD"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"},
        {"name": "STAR SPORTS 1 HD", "id": "StarSports1HD"},
        {"name": "ZEE BANGLA HD", "id": "ZeeBanglaHD"}
    ]
    
    m3u = "#EXTM3U\n"
    for ch in channels:
        stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
        m3u += f"#EXTINF:-1, {ch['name']}\n{stream_url}\n"
    return m3u

def update_github(content):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    res = requests.get(api_url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    content_encoded = base64.b64encode(content.encode()).decode()
    data = {"message": "Update Plusbox Playlist", "content": content_encoded, "sha": sha}
    
    requests.put(api_url, headers=headers, json=data)

if __name__ == "__main__":
    print("🚀 Fetching token...")
    token = get_plusbox_token()
    if token:
        playlist = generate_playlist(token)
        update_github(playlist)
        print(f"✅ Success! Token: {token[:10]}...")
    else:
        print("❌ Token Error: Could not fetch from Plusbox.")
