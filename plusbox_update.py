import requests
import re
import base64
import os
import time

# --- কনফিগারেশন ---
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
REPO_NAME = "nrjtvbd/plusbox" 
FILE_PATH = "playlist.m3u8"

def get_plusbox_token():
    url = "https://backend.plusbox.tv/BTVWorld/embed.html"
    # সেশন ব্যবহার করলে কুকি ম্যানেজমেন্ট সহজ হয়
    session = requests.Session()
    
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,image/avif,image/webp,*/*;q=0.8',
        'Referer': 'https://plusbox.tv/',
        'Origin': 'https://plusbox.tv',
        'Sec-Fetch-Dest': 'iframe',
        'Sec-Fetch-Mode': 'navigate',
        'Sec-Fetch-Site': 'same-origin'
    }

    for i in range(3): # ৩ বার চেষ্টা করবে
        try:
            response = session.get(url, headers=headers, timeout=20)
            if response.status_code == 200:
                match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
                if match:
                    return match.group(1)
            print(f"Attempt {i+1}: Status {response.status_code}")
            time.sleep(2) # ২ সেকেন্ড বিরতি
        except Exception as e:
            print(f"Attempt {i+1} Error: {e}")
    return None

def create_playlist(token):
    # আপনার আপলোড করা ফাইল থেকে চ্যানেলের নাম ও আইডি 
    channels = [
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "T SPORTS HD", "id": "TSportsHD"},
        {"name": "GAZI TV HD", "id": "GaziTVHD"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"},
        {"name": "STAR SPORTS 1 HD", "id": "StarSports1HD"},
        {"name": "ZEE BANGLA HD", "id": "ZeeBanglaHD"}
    ]
    
    m3u = "#EXTM3U\n"
    for ch in channels:
        # fmp4 স্ট্রিম ব্যবহার করা হয়েছে যাতে অডিও-ভিডিও একসাথে চলে 
        stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
        m3u += f"#EXTINF:-1, {ch['name']}\n{stream_url}\n"
    return m3u

def update_github(content):
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    res = requests.get(api_url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    content_encoded = base64.b64encode(content.encode()).decode()
    data = {
        "message": "Auto Update Plusbox Playlist",
        "content": content_encoded,
        "sha": sha
    }
    
    put_res = requests.put(api_url, headers=headers, json=data)
    if put_res.status_code in [200, 201]:
        print("✅ Playlist Updated on GitHub!")
    else:
        print(f"❌ GitHub Update Failed: {put_res.text}")

if __name__ == "__main__":
    print("🚀 Fetching Token...")
    token = get_plusbox_token()
    if token:
        print(f"✅ Token: {token[:10]}...")
        playlist_content = create_playlist(token)
        update_github(playlist_content)
    else:
        print("❌ Server is still blocking. Try changing the GH_TOKEN or Repo settings.")
