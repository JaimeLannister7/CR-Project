import requests
import json
import os

# আপনার API Key এবং প্লেয়ার লিস্ট (এগুলো আগের মতোই থাকবে)
API_KEY = "YOUR_API_KEY_HERE" 
PLAYER_FILE = "players.txt"
DATA_DIR = "Data"

def fetch_and_save():
    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)
    
    with open(PLAYER_FILE, "r") as f:
        tags = [line.strip() for line in f if line.strip()]

    summary_data = []

    for tag in tags:
        clean_tag = tag.replace("#", "")
        url = f"https://api.clashroyale.com/v1/players/%23{clean_tag}/battlelog"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        response = requests.get(url, headers=headers)
        if response.status_code == 200:
            new_battles = response.json()
            file_path = os.path.join(DATA_DIR, f"{clean_tag}.json")
            
            # আগের ডেটা লোড করা
            existing_battles = []
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    existing_battles = json.load(f)
            
            # নতুন ম্যাচ যোগ করা (ডুপ্লিকেট বাদ দিয়ে)
            all_battles = existing_battles
            existing_times = {b['battleTime'] for b in existing_battles}
            
            for battle in new_battles:
                if battle['battleTime'] not in existing_times:
                    all_battles.append(battle)
            
            with open(file_path, "w") as f:
                json.dump(all_battles, f, indent=4)
            
            # সামারির জন্য প্লেয়ারের নাম ও মোট ম্যাচ সংখ্যা রাখা
            player_name = all_battles[0]['team'][0]['name'] if all_battles else clean_tag
            summary_data.append({"name": player_name, "total_matches": len(all_battles)})

    # মোবাইল ড্যাশবোর্ডের জন্য সামারি ফাইল তৈরি
    with open(os.path.join(DATA_DIR, "summary.json"), "w") as f:
        json.dump(summary_data, f, indent=4)

fetch_and_save()
