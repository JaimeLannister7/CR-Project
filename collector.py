import requests
import json
import os
from collections import Counter

# আপনার API Key এবং প্লেয়ার লিস্ট
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
            
            existing_battles = []
            if os.path.exists(file_path):
                with open(file_path, "r") as f:
                    existing_battles = json.load(f)
            
            # নতুন ম্যাচ যোগ করা
            existing_times = {b['battleTime'] for b in existing_battles}
            for battle in new_battles:
                if battle['battleTime'] not in existing_times:
                    existing_battles.append(battle)
            
            with open(file_path, "w") as f:
                json.dump(existing_battles, f, indent=4)
            
            # --- বিস্তারিত এনালাইসিস শুরু ---
            wins = 0
            losses = 0
            draws = 0
            all_cards = []
            opponents = []
            current_win_streak = 0
            current_loss_streak = 0
            max_win_streak = 0
            max_loss_streak = 0
            
            # ম্যাচগুলো সময় অনুযায়ী সাজানো (পুরানো থেকে নতুন)
            existing_battles.sort(key=lambda x: x['battleTime'])
            
            for b in existing_battles:
                my_crowns = b['team'][0]['crowns']
                op_crowns = b['opponent'][0]['crowns']
                op_name = b['opponent'][0]['name']
                opponents.append(op_name)
                
                # কার্ড সংগ্রহ
                for card in b['team'][0]['cards']:
                    all_cards.append(card['name'])
                
                # হার-জিত ও স্ট্রাইক হিসাব
                if my_crowns > op_crowns:
                    wins += 1
                    current_win_streak += 1
                    max_win_streak = max(max_win_streak, current_win_streak)
                    current_loss_streak = 0
                elif my_crowns < op_crowns:
                    losses += 1
                    current_loss_streak += 1
                    max_loss_streak = max(max_loss_streak, current_loss_streak)
                    current_win_streak = 0
                else:
                    draws += 1
                    current_win_streak = 0
                    current_loss_streak = 0

            # টপ ৫ কার্ড এবং প্রধান প্রতিপক্ষ
            top_cards = [c[0] for c in Counter(all_cards).most_common(5)]
            top_opponent = Counter(opponents).most_common(1)[0][0] if opponents else "N/A"
            player_name = existing_battles[-1]['team'][0]['name'] if existing_battles else clean_tag

            summary_data.append({
                "name": player_name,
                "total": len(existing_battles),
                "win": wins,
                "loss": losses,
                "draw": draws,
                "win_streak": max_win_streak,
                "loss_streak": max_loss_streak,
                "top_cards": ", ".join(top_cards),
                "rival": top_opponent
            })

    # সামারি ফাইল সেভ করা (এটিই মোবাইলে দেখাবে)
    with open(os.path.join(DATA_DIR, "summary.json"), "w") as f:
        json.dump(summary_data, f, indent=4)

fetch_and_save()
