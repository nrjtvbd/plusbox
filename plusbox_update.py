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
    # আপনার দেওয়া তথ্য অনুযায়ী সোর্স ইউআরএল
    url = "https://backend.plusbox.tv/BTVWorld/embed.html"
    session = requests.Session()
    
    # আপনার দেওয়া হুবহু হেডার যা ব্রাউজার ব্যবহার করছে
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Accept': '*/*',
        'Accept-Encoding': 'gzip, deflate, br, zstd',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://plusbox.tv/',
        'Origin': 'https://plusbox.tv',
        'Sec-Ch-Ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'empty',
        'Sec-Fetch-Mode': 'cors',
        'Sec-Fetch-Site': 'same-origin',
        'Connection': 'keep-alive'
    }

    try:
        # কুকি ভ্যালিডেশনের জন্য প্রথমে মেইন পেজ ভিজিট
        session.get("https://plusbox.tv/", headers={'User-Agent': headers['User-Agent']}, timeout=15)
        
        # এবার টোকেনের জন্য এমবেড পেজে রিকোয়েস্ট
        # প্লাসবক্স এখন হেডার খুব কড়াকড়িভাবে চেক করে, তাই headers=headers দেওয়া জরুরি
        response = session.get(url, headers=headers, timeout=25)
        
        if response.status_code == 200:
            # রেজেক্স দিয়ে টোকেন খুঁজে বের করা
            match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
            if match:
                return match.group(1)
            else:
                print("⚠️ Token string not found in HTML response.")
        else:
            print(f"❌ Server blocked with status: {response.status_code}")
            
        return None
    except Exception as e:
        print(f"📡 Connection Error: {e}")
        return None

def update_github(token):
    # চ্যানেল লিস্ট (ID গুলো আপনার দেওয়া plusboxtv.txt অনুযায়ী)
    channels = [
        {"name": "T-SPORTS HD", "id": "TSportsHD"},
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "GAZI TV HD", "id": "GaziTVHD"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"}
    ]

    m3u_content = "#EXTM3U\n"
    for ch in channels:
        # আপনার দেওয়া Master URL ফরম্যাট অনুযায়ী লিঙ্ক জেনারেট
        stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
        m3u_content += f"#EXTINF:-1, {ch['name']}\n{stream_url}\n"

    # GitHub API এর মাধ্যমে ফাইল আপডেট
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    git_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # বর্তমান ফাইলের SHA সংগ্রহ
    res = requests.get(api_url, headers=git_headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    encoded = base64.b64encode(m3u_content.encode()).decode()
    payload = {
        "message": "⚡ System Update: Auto-refreshing playlist with new token",
        "content": encoded,
        "sha": sha
    }
    
    put_res = requests.put(api_url, headers=git_headers, json=payload)
    if put_res.status_code in [200, 201]:
        print("✅ Success! Playlist updated on GitHub.")
    else:
        print(f"❌ GitHub Update Failed: {put_res.text}")

if __name__ == "__main__":
    print("🛰️ Initializing bypass sequence...")
    token = get_plusbox_token()
    if token:
        print(f"🔑 New Token Acquired: {token[:20]}...")
        update_github(token)
    else:
        print("🛑 Bypass failed. Server is detecting the Cloud environment.")
