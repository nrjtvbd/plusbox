import requests
import base64
import os

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox" 
FILE_PATH = "playlist.m3u8"
# গুগল স্ক্রিপ্টের লিঙ্কটি এখানে দিন
GAS_URL = "https://script.google.com/macros/s/AKfycbxqEzYDuis3g9RLJ9Ha9qocHWBZUqJiC9_yTJcQOjD-Ri-9Yaqx1iKfw7F8O7gHAxjR/exec" 

def get_token_from_google():
    try:
        print(f"📡 Requesting token via Google Tunnel...")
        # Google Script রিডাইরেক্ট করে, তাই allow_redirects=True রাখতে হবে
        response = requests.get(GAS_URL, allow_redirects=True, timeout=30)
        if response.status_code == 200 and "Token_Not_Found" not in response.text:
            return response.text.strip()
        print(f"⚠️ Google couldn't find token. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Google Tunnel Error: {e}")
    return None

def update_github(token):
    channels = [
        {"name": "T-SPORTS HD", "id": "TSportsHD"},
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "GAZI TV HD", "id": "GaziTVHD"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"}
    ]

    m3u = "#EXTM3U\n"
    for ch in channels:
        url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
        m3u += f"#EXTINF:-1, {ch['name']}\n{url}\n"

    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    git_headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    res = requests.get(api_url, headers=git_headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    encoded = base64.b64encode(m3u.encode()).decode()
    payload = {
        "message": "Update: Fetched via Google Apps Script Tunnel",
        "content": encoded,
        "sha": sha
    }
    requests.put(api_url, headers=git_headers, json=payload)

if __name__ == "__main__":
    token = get_token_from_google()
    if token:
        print(f"✅ Token Received: {token[:15]}...")
        update_github(token)
        print("✅ GitHub Updated via Google Tunnel!")
    else:
        print("❌ Everything failed. Plusbox is blocking Google too.")
