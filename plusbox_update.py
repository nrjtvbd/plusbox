import requests
import re
import base64
import os
import time

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox" 
FILE_PATH = "playlist.m3u8"

def get_plusbox_token():
    # সরাসরি এমবেড ইউআরএল এর বদলে প্লাসবক্সের ডাটা গেটওয়ে ট্রাই করা হচ্ছে
    url = "https://backend.plusbox.tv/BTVWorld/embed.html"
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/124.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Referer': 'https://plusbox.tv/',
        'Origin': 'https://plusbox.tv',
        'Sec-Ch-Ua': '"Chromium";v="124", "Google Chrome";v="124", "Not-A.Brand";v="99"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"'
    }

    try:
        # কুকি জেনারেট করার জন্য প্রথমে মেইন সাইটে একবার হিট করা
        session.get("https://plusbox.tv/", headers={'User-Agent': headers['User-Agent']}, timeout=10)
        
        # এবার টোকেনের জন্য রিকোয়েস্ট
        response = session.get(url, headers=headers, timeout=20)
        
        if response.status_code == 200:
            match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
            if match:
                return match.group(1)
        
        print(f"Server Response: {response.status_code}")
        return None
    except Exception as e:
        print(f"Request Error: {e}")
        return None

def update_github(token):
    # চ্যানেল লিস্ট তৈরি (আপনি চাইলে plusboxtv.txt থেকেও নিতে পারেন)
    channels = [
        {"name": "T-SPORTS HD", "id": "TSportsHD"},
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "GAZI TV HD", "id": "GaziTVHD"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"}
    ]

    m3u_content = "#EXTM3U\n"
    for ch in channels:
        stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
        m3u_content += f"#EXTINF:-1, {ch['name']}\n{stream_url}\n"

    # GitHub Update Logic
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    get_res = requests.get(api_url, headers=headers)
    sha = get_res.json().get('sha') if get_res.status_code == 200 else None
    
    encoded_content = base64.b64encode(m3u_content.encode()).decode()
    data = {"message": "Update Playlist", "content": encoded_content, "sha": sha}
    
    requests.put(api_url, headers=headers, json=data)

if __name__ == "__main__":
    print("🚀 Fetching dynamic token...")
    token = get_plusbox_token()
    if token:
        print(f"✅ Token Found: {token[:10]}...")
        update_github(token)
        print("✅ GitHub File Updated!")
    else:
        print("❌ Token Error. Plusbox is still blocking GitHub Actions IP.")
