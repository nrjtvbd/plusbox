import requests
import re
import base64
import os

# গিটহাব থেকে সিক্রেট হিসেবে টোকেনটি নেওয়া হবে
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox" 
FILE_PATH = "plusbox.m3u8"

def get_plusbox_token():
    url = "https://backend.plusbox.tv/BTVWorld/embed.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36',
        'Referer': 'https://plusbox.tv/'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        # টোকেন খোঁজার লজিক
        match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
        return match.group(1) if match else None
    except:
        return None

def generate_playlist(token):
    # আপনার দেওয়া সোর্স ফাইল থেকে প্রধান চ্যানেলগুলোর লিস্ট [cite: 10, 11, 20, 38, 42]
    channels = [
        {"name": "T-SPORTS HD", "id": "TSportsHD"},
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"},
        {"name": "GAZI TV HD", "id": "GaziTVHD"},
        {"name": "STAR SPORTS 1 HD", "id": "StarSports1HD"},
        {"name": "ZEE BANGLA HD", "id": "ZeeBanglaHD"}
    ]
    
    m3u = "#EXTM3U\n"
    for ch in channels:
        # index.fmp4.m3u8 ব্যবহার করলে অডিও এবং ভিডিও একটি লিঙ্কেই কাজ করবে 
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
    token = get_plusbox_token()
    if token:
        playlist = generate_playlist(token)
        update_github(playlist)
        print("✅ Success!")
    else:
        print("❌ Token Error")
