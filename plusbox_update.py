import requests
import base64
import os

# --- CONFIG ---
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox"
FILE_PATH = "playlist.m3u8"
GAS_URL = "https://script.google.com/macros/s/AKfycbyo2ttERRFa-r5DNJBaHnL8sDrDtnX3BPRzunlhCMET_yQcyyK42K4Kzzdd_DPOAak/exec"

def get_valid_token():
    print("📡 Contacting Google Tunnel...")
    try:
        res = requests.get(GAS_URL, allow_redirects=True, timeout=30)
        token = res.text.strip()
        
        # যাচাই করা হচ্ছে এটা কি আসলেই টোকেন নাকি কোনো এরর মেসেজ
        if token and len(token) > 20 and "_" not in token and "Error" not in token:
            return token
        print(f"⚠️ Invalid data received from tunnel: {token[:30]}")
    except Exception as e:
        print(f"❌ Connection failed: {e}")
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
        m3u += f"#EXTINF:-1, {ch['name']}\nhttps://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}\n"

    api_url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {"Authorization": f"token {GITHUB_TOKEN}"}
    
    # SHA সংগ্রহ
    res = requests.get(api_url, headers=headers)
    sha = res.json().get('sha') if res.status_code == 200 else None
    
    encoded = base64.b64encode(m3u.encode()).decode()
    data = {"message": "⚡ Automated Token Refresh", "content": encoded, "sha": sha}
    
    final_res = requests.put(api_url, headers=headers, json=data)
    if final_res.status_code in [200, 201]:
        print("✅ Playlist updated successfully with a VALID token!")
    else:
        print(f"❌ Update failed: {final_res.text}")

if __name__ == "__main__":
    token = get_valid_token()
    if token:
        print(f"🔑 Valid Token Found: {token[:15]}...")
        update_github(token)
    else:
        print("🛑 Script stopped: No valid token available at this moment.")
