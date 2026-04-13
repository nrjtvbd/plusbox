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
    url = "https://backend.plusbox.tv/BTVWorld/embed.html"
    
    # ব্রাউজার হেডার (আপনার দেওয়া তথ্য অনুযায়ী)
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Referer': 'https://plusbox.tv/',
        'Sec-Ch-Ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin'
    }

    # একটি ফ্রী প্রক্সি এপিআই ব্যবহার করে চেষ্টা করা (যেমন: ScraperAnt বা সাধারণ Proxy)
    # এখানে আমরা সরাসরি রিকোয়েস্ট পাঠানোর বদলে একটি প্রক্সি গেটওয়ে ব্যবহার করছি
    proxy_url = f"https://api.allorigins.win/get?url={url}"

    try:
        print("🌐 Trying to fetch token via Proxy Gateway...")
        response = requests.get(proxy_url, timeout=30)
        
        if response.status_code == 200:
            data = response.json()
            page_content = data.get('contents', '')
            
            # টোকেন খোঁজা
            match = re.search(r'token=([a-zA-Z0-9\-_.]+)', page_content)
            if match:
                return match.group(1)
        
        print(f"⚠️ Proxy method failed or returned no token. Status: {response.status_code}")
        return None
    except Exception as e:
        print(f"📡 Proxy Error: {e}")
        return None

def update_github(token):
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

    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    git_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    res = requests.get(api_url, headers=git_headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    encoded = base64.b64encode(m3u_content.encode()).decode()
    payload = {
        "message": "Update: Bypassed with Proxy Gateway",
        "content": encoded,
        "sha": sha
    }
    
    requests.put(api_url, headers=git_headers, json=payload)

if __name__ == "__main__":
    token = get_plusbox_token()
    if token:
        print(f"✅ Token Found via Proxy: {token[:20]}...")
        update_github(token)
        print("✅ Playlist Updated!")
    else:
        print("❌ All methods failed. Plusbox is extremely secured against Cloud IPs.")
