import requests
import re
import base64
import os
import time
import random

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox" 
FILE_PATH = "playlist.m3u8"

def get_plusbox_token():
    session = requests.Session()
    
    # আপনার দেওয়া ডাটা অনুযায়ী একদম লেটেস্ট হেডার
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/146.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,image/apng,*/*;q=0.8,application/signed-exchange;v=b3;q=0.7',
        'Accept-Language': 'en-US,en;q=0.9',
        'Referer': 'https://plusbox.tv/',
        'Origin': 'https://plusbox.tv',
        'Sec-Ch-Ua': '"Chromium";v="146", "Not-A.Brand";v="24", "Google Chrome";v="146"',
        'Sec-Ch-Ua-Mobile': '?0',
        'Sec-Ch-Ua-Platform': '"Windows"',
        'Sec-Fetch-Dest': 'iframe', # আপনার ডাটা অনুযায়ী এটি iframe হবে
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin',
        'Upgrade-Insecure-Requests': '1',
        'Connection': 'keep-alive'
    }

    try:
        # Step 1: মূল সাইটে হিট করে কুকি সেট করা
        print("🔍 Visiting main site...")
        session.get("https://plusbox.tv/", headers={'User-Agent': headers['User-Agent']}, timeout=15)
        
        # মানুষের মতো আচরণ করার জন্য ২-৫ সেকেন্ড ওয়েট
        time.sleep(random.uniform(2, 5))
        
        # Step 2: টোকেনের জন্য এমবেড পেজে হিট করা
        print("🛰️ Requesting token with Chrome 146 headers...")
        url = "https://backend.plusbox.tv/BTVWorld/embed.html"
        response = session.get(url, headers=headers, timeout=25)
        
        if response.status_code == 200:
            token_match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
            if token_match:
                return token_match.group(1)
            else:
                # যদি সরাসরি না পাওয়া যায়, তবে রেসপন্স টেক্সট চেক করা
                print("⚠️ Token not in plain text, checking alternative patterns...")
                alt_match = re.search(r'["\']([a-zA-Z0-9\-_]{50,})["\']', response.text)
                return alt_match.group(1) if alt_match else None
        
        print(f"❌ Blocked! Status: {response.status_code}")
        return None

    except Exception as e:
        print(f"📡 Connection Error: {e}")
        return None

def push_to_github(token):
    channels = [
        {"name": "T-SPORTS HD", "id": "TSportsHD"},
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "GAZI TV HD", "id": "GaziTVHD"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"}
    ]

    m3u_content = "#EXTM3U\n"
    for ch in channels:
        # আপনার দেওয়া Master URL ফরম্যাট
        url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
        m3u_content += f"#EXTINF:-1, {ch['name']}\n{url}\n"

    # GitHub Update
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    git_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    res = requests.get(api_url, headers=git_headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    encoded = base64.b64encode(m3u_content.encode()).decode()
    payload = {
        "message": "Update: Bypassing security with new headers",
        "content": encoded,
        "sha": sha
    }
    
    requests.put(api_url, headers=git_headers, json=payload)
    print("✅ Playlist successfully updated!")

if __name__ == "__main__":
    token = get_plusbox_token()
    if token:
        print(f"🔑 Token Found: {token[:25]}...")
        push_to_github(token)
    else:
        print("❌ Still blocked. Plusbox firewalls are detecting the GitHub Action IP range.")
