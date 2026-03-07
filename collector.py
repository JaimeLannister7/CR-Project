import requests
import json
import os
from collections import Counter
from datetime import datetime

API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjlkNWE1NTQ5LWZhM2YtNDJiNS05YzM3LTdjZjYzOWQ4NGNlNSIsImlhdCI6MTc3MjgxNDcwNywic3ViIjoiZGV2ZWxvcGVyLzY4ODAxNjIxLWI4NjgtYjA1OC0zZTI5LWRhMDNhNGMzN2U0YiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMDMuMTcwLjE3My4zNCJdLCJ0eXBlIjoiY2xpZW50In1dfQ.nfL5j_cVAJtnuIZwN0YoQtvUyrd0uBSYfpBwbl1bIvJ2rxFOEbTKZvraMWJQSZqJTRP7iOM3MSDloBW017nKtg"
PLAYER_FILE = "players.txt"
DATA_DIR = "Data"

SPELLS = ["Zap", "The Log", "Fireball", "Arrows", "Rocket", "Lightning", "Poison", "Freeze", "Tornado", "Earthquake", "Barbarian Barrel", "Giant Snowball", "Royal Delivery", "Void", "Rage", "Mirror", "Clone", "Graveyard", "Heal Spirit"]
BUILDINGS = ["Cannon", "Inferno Tower", "Tesla", "Elixir Collector", "Goblin Cage", "Bomb Tower", "Mortar", "X-Bow", "Barbarian Hut", "Goblin Hut", "Furnace", "Goblin Drill", "Cannon Cart"]

def fetch_and_save():
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    with open(PLAYER_FILE, "r") as f: tags = [line.strip() for line in f if line.strip()]
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
                with open(file_path, "r") as f: existing_battles = json.load(f)
            
            existing_times = {b['battleTime'] for b in existing_battles}
            for battle in new_battles:
                if battle['battleTime'] not in existing_times: existing_battles.append(battle)
            
            existing_battles.sort(key=lambda x: x['battleTime'])
            with open(file_path, "w") as f: json.dump(existing_battles, f, indent=4)
            
            # --- এনালাইসিস ---
            wins, losses, draws = 0, 0, 0
            units, spells, buildings = [], [], []
            played_rivals, won_rivals, lost_rivals, draw_rivals = [], [], [], []
            win_s, loss_s, max_w, max_l = 0, 0, 0, 0
            
            last_match_time = "Never"
            if existing_battles:
                raw_time = existing_battles[-1]['battleTime']
                dt = datetime.strptime(raw_time, '%Y%m%dT%H%M%S.%fZ')
                last_match_time = dt.strftime('%d %b, %I:%M %p')

            for b in existing_battles:
                my_c, op_c, op_name = b['team'][0]['crowns'], b['opponent'][0]['crowns'], b['opponent'][0]['name']
                played_rivals.append(op_name)
                for card in b['team'][0]['cards']:
                    name = card['name']
                    if name in SPELLS: spells.append(name)
                    elif name in BUILDINGS: buildings.append(name)
                    else: units.append(name)
                
                if my_c > op_c:
                    wins += 1; won_rivals.append(op_name); win_s += 1; max_w = max(max_w, win_s); loss_s = 0
                elif my_c < op_c:
                    losses += 1; lost_rivals.append(op_name); loss_s += 1; max_l = max(max_l, loss_s); win_s = 0
                else:
                    draws += 1; draw_rivals.append(op_name); win_s = 0; loss_s = 0

            def get_top(arr, count=1): 
                res = [c[0] for c in Counter(arr).most_common(count)]
                return ", ".join(res) if res else "None"

            summary_data.append({
                "name": existing_battles[-1]['team'][0]['name'] if existing_battles else clean_tag,
                "total": len(existing_battles),
                "win": wins, "loss": losses, "draw": draws,
                "w_s": max_w, "l_s": max_l,
                "top_units": get_top(units, 5),
                "top_spells": get_top(spells, 5), # ৫টি স্পেল
                "top_buildings": get_top(buildings, 5), # ৫টি বিল্ডিং
                "last_match": last_match_time,
                "h_played": get_top(played_rivals),
                "h_win": get_top(won_rivals), "h_loss": get_top(lost_rivals), "h_draw": get_top(draw_rivals)
            })

    with open(os.path.join(DATA_DIR, "summary.json"), "w") as f: json.dump(summary_data, f, indent=4)

fetch_and_save()
