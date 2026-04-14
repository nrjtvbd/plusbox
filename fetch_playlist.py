import datetime

# --- CONFIGURATION ---
# আপনার ব্রাউজার বা লগ থেকে পাওয়া সচল টোকেনটি এখানে বসান
BACKUP_TOKEN = "429c3921a2fd76dc77e7e39e440b8e7616c52327-06c5179800988e5db9acb5f98f7f8567-1776205375-1776194575"

CHANNELS = [
    {"id": "BTVWorld", "name": "BTV WORLD"},
    {"id": "GTV", "name": "GAZI TV HD"},
    {"id": "StarJalsha", "name": "STAR JALSHA HD"},
    {"id": "SonyTen1", "name": "SONY TEN 1 HD"}
]

def main():
    print("🚀 Generating Playlist using Backup Token...")
    entries = []
    
    for ch in CHANNELS:
        # মাস্টার ইউআরএল ফরম্যাট অনুযায়ী লিঙ্ক তৈরি
        stream_url = f"https://backend.plusbox.tv/{ch['id']}/index.fmp4.m3u8?token={BACKUP_TOKEN}"
        entries.append(f'#EXTINF:-1 tvg-name="{ch["name"]}",{ch["name"]}\n{stream_url}')
        print(f"✅ Added: {ch['name']}")

    # প্লেলিস্ট ফাইল তৈরি
    header = f"#EXTM3U\n# Last Sync: {datetime.datetime.now().strftime('%Y-%m-%d %H:%M:%S')}\n# Source: Backup Token\n"
    with open("playlist.m3u", "w") as f:
        f.write(header + "\n".join(entries))
    
    print("\n🎉 Playlist generated with the provided backup token!")

if __name__ == "__main__":
    main()
