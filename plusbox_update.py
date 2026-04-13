import requests
import re
import base64
import os
import json

# --- CONFIGURATION ---
GITHUB_TOKEN = os.getenv("GH_TOKEN")
REPO_NAME = "nrjtvbd/plusbox"  # আপনার রেপো নাম
M3U_FILENAME = "playlist.m3u8"
SOURCE_FILE = "plusboxtv.txt"  # এই ফাইল থেকে চ্যানেল ডাটা রিড করবে

def get_token():
    """Plusbox থেকে লেটেস্ট টোকেন বের করার মেথড"""
    url = "https://backend.plusbox.tv/BTVWorld/embed.html"
    headers = {
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/123.0.0.0 Safari/537.36',
        'Referer': 'https://plusbox.tv/',
        'Origin': 'https://plusbox.tv'
    }
    try:
        # সরাসরি requests দিয়ে ট্রাই করা হচ্ছে (403 এড়াতে উন্নত হেডারসহ)
        response = requests.get(url, headers=headers, timeout=20)
        if response.status_code == 200:
            match = re.search(r'token=([a-zA-Z0-9\-_.]+)', response.text)
            if match:
                return match.group(1)
        return None
    except:
        return None

def extract_channels_from_file(filename):
    """আপনার আপলোড করা plusboxtv.txt থেকে চ্যানেল আইডি ও নাম সংগ্রহ করবে"""
    channels = []
    if not os.path.exists(filename):
        # যদি ফাইল না থাকে, তবে ডিফল্ট কিছু চ্যানেল ব্যবহার করবে
        return [
            {"id": "TSportsHD", "title": "T-Sports HD"},
            {"id": "BTVWorld", "title": "BTV World"},
            {"name": "GaziTVHD", "id": "Gazi TV HD"}
        ]

    with open(filename, 'r', encoding='utf-8') as f:
        content = f.read()
    
    # আপনার টেক্সট ফাইলের ফরম্যাট অনুযায়ী আইডি খুঁজে বের করার লজিক
    # যেমন: /TSportsHD/embed.html থেকে 'TSportsHD' আইডি নিবে
    pattern = r'/([a-zA-Z0-9]+)/embed\.html'
    matches = re.findall(pattern, content)
    
    # ডুপ্লিকেট রিমুভ করে লিস্ট তৈরি
    unique_ids = list(set(matches))
    for ch_id in unique_ids:
        channels.append({
            "id": ch_id,
            "title": ch_id.replace("HD", " HD").upper() # আইডি থেকে সুন্দর নাম তৈরি
        })
    return channels

def update_github(content):
    """GitHub API ব্যবহার করে ফাইল পুশ করার মেথড"""
    url = f"https://api.github.com/repos/{REPO_NAME}/contents/{M3U_FILENAME}"
    headers = {
        "Authorization": f"token {GITHUB_TOKEN}",
        "Accept": "application/vnd.github.v3+json"
    }

    # ফাইল থাকলে SHA নিবে, না থাকলে নতুন তৈরি করবে
    get_res = requests.get(url, headers=headers)
    sha = get_res.json().get('sha') if get_res.status_code == 200 else None

    base64_content = base64.b64encode(content.encode("utf-8")).decode("utf-8")

    data = {
        "message": "System Update: Plusbox Playlist Refresh",
        "content": base64_content,
        "sha": sha
    }

    put_res = requests.put(url, headers=headers, json=data)
    return put_res.status_code

def main():
    print("🚀 Process Started...")
    
    # ১. টোকেন সংগ্রহ
    token = get_token()
    if not token:
        print("❌ Token Fetching Failed! (403 or Timeout)")
        return

    print(f"✅ Token Found: {token[:15]}...")

    # ২. চ্যানেল এক্সট্রাকশন (ফাইল থেকে)
    channels = extract_channels_from_file(SOURCE_FILE)
    
    # ৩. M3U8 প্লেলিস্ট তৈরি
    m3u_content = "#EXTM3U\n"
    for ch in channels:
        # অডিও-ভিডিও একসাথে পাওয়ার জন্য index.fmp4.m3u8 ব্যবহার
        stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={token}"
        m3u_content += f"#EXTINF:-1, {ch['title']}\n{stream_url}\n"

    # ৪. গিটহাবে আপলোড
    status = update_github(m3u_content)
    
    if status in [200, 201]:
        print(f"✅ Status: Online. {M3U_FILENAME} updated successfully!")
    else:
        print(f"❌ GitHub Update Failed with status: {status}")

if __name__ == "__main__":
    main()
