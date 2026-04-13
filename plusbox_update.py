import requests
import re
import base64
import os

# --- GitHub Configuration ---
# Apnar GitHub Secret-e 'GH_TOKEN' name token-ti thakte hobe
GITHUB_TOKEN = os.getenv("GH_TOKEN") 
REPO_NAME = "nrjtvbd/plusbox"  # Apnar repo name
FILE_PATH = "playlist.m3u8"    # Jei name playlist save hobe

def get_plusbox_token():
    """Plusbox theke dynamic token sangraha korar method"""
    url = "https://backend.plusbox.tv/BTVWorld/embed.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://plusbox.tv/',
        'Origin': 'https://plusbox.tv'
    }
    try:
        response = requests.get(url, headers=headers, timeout=15)
        if response.status_code == 200:
            # Regex diye token khuje ber kora
            match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
            if match:
                return match.group(1)
        return None
    except Exception as e:
        print(f"Token Error: {e}")
        return None

def create_m3u8_playlist(token):
    """Token bebohar kore puronago M3U8 content toiri korar method"""
    # Apnar deya list onujayi channel gulo
    channels = [
        {"name": "T-SPORTS HD", "id": "TSportsHD"},
        {"name": "T-SPORTS", "id": "TSports"},
        {"name": "Gazi TV HD", "id": "GaziTVHD"},
        {"name": "BTV WORLD", "id": "BTVWorld"},
        {"name": "STAR JALSHA HD", "id": "StarJalshaHD"},
        {"name": "SONY TEN 1 HD", "id": "SonyTen1HD"},
        {"name": "SONY TEN 2 HD", "id": "SonyTen2HD"},
        {"name": "SONY MAX HD", "id": "SonyMaxHD"},
        {"name": "ZEE BANGLA HD", "id": "ZeeBanglaHD"},
        {"name": "COLORS BANGLA", "id": "ColorsBangla"}
    ]
    
    m3u_content = "#EXTM3U\n"
    for ch in channels:
        # Link structure: https://backend.plusbox.tv/{ID}/index.fmp4.m3u8?token={TOKEN}
        stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
        m3u_content += f"#EXTINF:-1, {ch['name']}\n{stream_url}\n"
    
    return m3u_content

def update_github_file(content):
    """GitHub API bebohar kore file update korar method"""
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{FILE_PATH}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # 1. Purono file-er SHA neya (update korar jonno dorkar)
    get_res = requests.get(url, headers=headers)
    sha = get_res.json().get('sha') if get_res.status_code == 200 else None

    # 2. Content-ke Base64 encode kora
    base64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": "Auto Update Plusbox Playlist",
        "content": base64_content,
        "sha": sha
    }

    # 3. File upload/update kora
    put_res = requests.put(url, headers=headers, json=data)
    if put_res.status_code in [200, 201]:
        print("✅ Playlist Successfully Updated on GitHub!")
    else:
        print(f"❌ Failed to update GitHub: {put_res.text}")

if __name__ == "__main__":
    print("Step 1: Fetching Token...")
    token = get_plusbox_token()
    
    if token:
        print(f"✅ Token Found: {token[:15]}...")
        print("Step 2: Creating M3U8 Playlist...")
        playlist = create_m3u8_playlist(token)
        
        print("Step 3: Uploading to GitHub...")
        update_github_file(playlist)
    else:
        print("❌ Token not found! Server might be blocking the request.")
