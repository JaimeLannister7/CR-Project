import requests
import json
import os
from collections import Counter

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
            
            existing_times = {b['battleTime'] for b in existing_battles}
            for battle in new_battles:
                if battle['battleTime'] not in existing_times:
                    existing_battles.append(battle)
            
            with open(file_path, "w") as f:
                json.dump(existing_battles, f, indent=4)
            
            # --- বিস্তারিত ডাটা ক্যালকুলেশন ---
            wins, losses, draws = 0, 0, 0
            all_cards, played_rivals, won_rivals, lost_rivals, draw_rivals = [], [], [], [], []
            win_streak, loss_streak, max_win_s, max_loss_s = 0, 0, 0, 0
            
            existing_battles.sort(key=lambda x: x['battleTime'])
            
            for b in existing_battles:
                my_c = b['team'][0]['crowns']
                op_c = b['opponent'][0]['crowns']
                op_name = b['opponent'][0]['name']
                played_rivals.append(op_name)
                
                for card in b['team'][0]['cards']:
                    all_cards.append(card['name'])
                
                if my_c > op_c:
                    wins += 1
                    won_rivals.append(op_name)
                    win_streak += 1
                    max_win_s = max(max_win_s, win_streak)
                    loss_streak = 0
                elif my_c < op_c:
                    losses += 1
                    lost_rivals.append(op_name)
                    loss_streak += 1
                    max_loss_s = max(max_loss_s, loss_streak)
                    win_streak = 0
                else:
                    draws += 1
                    draw_rivals.append(op_name)
                    win_streak = 0
                    loss_streak = 0

            def get_top(arr): return Counter(arr).most_common(1)[0][0] if arr else "N/A"
            top_cards = [c[0] for c in Counter(all_cards).most_common(5)]
            player_name = existing_battles[-1]['team'][0]['name'] if existing_battles else clean_tag

            summary_data.append({
                "name": player_name,
                "total": len(existing_battles),
                "win": wins, "loss": losses, "draw": draws,
                "w_s": max_win_s, "l_s": max_loss_s,
                "top_cards": ", ".join(top_cards),
                "h_played": get_top(played_rivals),
                "h_win": get_top(won_rivals),
                "h_loss": get_top(lost_rivals),
                "h_draw": get_top(draw_rivals)
            })

    with open(os.path.join(DATA_DIR, "summary.json"), "w") as f:
        json.dump(summary_data, f, indent=4)

fetch_and_save()
