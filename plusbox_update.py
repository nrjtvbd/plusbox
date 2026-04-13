import requests
import base64
import os
import time

# --- CONFIG ---
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox"
FILE_PATH = "playlist.m3u8"
# আপনার নতুন Google Script URL এখানে দিন
GAS_URL = "https://script.google.com/macros/s/AKfycbwIG3ioOqUZJp7fXVTDd1GkOQrSCapVu9eE0B1S-PlCqf1UQJWO3cakWTm5xSIjjqfo/exec"

def get_token():
    print("📡 Contacting Google Tunnel for Token...")
    try:
        # Google Apps Script রিডাইরেক্ট করে, তাই allow_redirects জরুরি
        res = requests.get(GAS_URL, allow_redirects=True, timeout=30)
        token = res.text.strip()
        if token and len(token) > 20 and "Token_Not_Found" not in token:
            return token
        print(f"⚠️ Response from Google: {token[:50]}")
    except Exception as e:
        print(f"❌ Connection Error: {e}")
    return None

def update_github(token):
    # চ্যানেল লিস্ট
    channels = [
        {"name": "T-SPORTS HD", "id": "TSportsHD"},
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "GAZI TV HD", "id": "GaziTVHD"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"}
    ]

    m3u = "#EXTM3U\n"
    for ch in channels:
        # Master Stream URL
        m3u += f"#EXTINF:-1, {ch['name']}\nhttps://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}\n"

    # GitHub Update
    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    get_res = requests.get(api_url, headers=headers)
    sha = get_res.json().get('sha') if get_res.status_code == 200 else None
    
    encoded = base64.b64encode(m3u.encode()).decode()
    data = {"message": "⚡ Auto-refresh via Google Tunnel", "content": encoded, "sha": sha}
    
    final_res = requests.put(api_url, headers=headers, json=data)
    if final_res.status_code in [200, 201]:
        print("✅ Playlist Successfully Updated on GitHub!")
    else:
        print(f"❌ GitHub Update Failed: {final_res.text}")

if __name__ == "__main__":
    new_token = get_token()
    if new_token:
        print(f"🔑 New Token: {new_token[:15]}...")
        update_github(new_token)
    else:
        print("🛑 All tunnels failed. Plusbox is using JS-based token generation.")
