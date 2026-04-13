import requests
import base64
import os

GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox" 
FILE_PATH = "playlist.m3u8"
# আপনার ওয়ার্কার লিঙ্কটি এখানে দিন (নিচেরটি উদাহরণ)
WORKER_URL = "https://plusbox.drrkrana.workers.dev" 

def get_token_from_worker():
    try:
        print(f"📡 Requesting token from Cloudflare Worker...")
        response = requests.get(WORKER_URL, timeout=20)
        if response.status_code == 200 and "Token_Not_Found" not in response.text:
            return response.text.strip()
        print(f"⚠️ Worker couldn't find token. Status: {response.status_code}")
    except Exception as e:
        print(f"❌ Worker Error: {e}")
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
        "message": "Update: Fetched via Worker Tunnel",
        "content": encoded,
        "sha": sha
    }
    requests.put(api_url, headers=git_headers, json=payload)

if __name__ == "__main__":
    token = get_token_from_worker()
    if token:
        print(f"✅ Token Received: {token[:15]}...")
        update_github(token)
        print("✅ GitHub Updated!")
    else:
        print("❌ Still failing. Plusbox is blocking Cloudflare too.")
