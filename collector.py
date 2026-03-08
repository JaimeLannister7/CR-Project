import requests
import json
import os
from collections import Counter
from datetime import datetime

# আপনার একদম নতুন এবং সঠিক Key সরাসরি এখানে বসানো হলো
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjhkOGM5YTk1LTNkMzMtNDg2Zi04MmUzLWNmY2M4MzkxZDAyNSIsImlhdCI6MTc3Mjk1OTYwNCwic3ViIjoiZGV2ZWxvcGVyLzY4ODAxNjIxLWI4NjgtYjA1OC0zZTI5LWRhMDNhNGMzN2U0YiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMjguMTk5LjIzMS41NyJdLCJ0eXBlIjoiY2xpZW50In1dfQ.RvbaDf-PhkqLE5VuTUz8OwIsen1tKFy1yQHGKtID0j5gdGgeijZ7ug4xwqe3eYRjCs1lazPEvzcPaC3R6eGffg"

PLAYER_FILE = "players.txt"
DATA_DIR = "Data"

# কার্ডের ক্যাটাগরিগুলো
SPELLS = ["Zap","The Log","Fireball","Arrows","Rocket","Lightning","Poison","Freeze","Tornado","Earthquake","Barbarian Barrel","Giant Snowball","Royal Delivery","Void","Rage","Mirror","Clone","Graveyard","Heal Spirit"]
BUILDINGS = ["Cannon","Inferno Tower","Tesla","Elixir Collector","Goblin Cage","Bomb Tower","Mortar","X-Bow","Barbarian Hut","Goblin Hut","Furnace","Goblin Drill","Cannon Cart"]

def fetch_and_save():
    if not os.path.exists(DATA_DIR): os.makedirs(DATA_DIR)
    if not os.path.exists(PLAYER_FILE): return

    with open(PLAYER_FILE,"r") as f:
        tags = [line.strip() for line in f if line.strip()]

    summary_data = []

    for tag in tags:
        clean_tag = tag.replace("#", "")
        # RoyaleAPI Proxy লিঙ্ক
        url = f"https://proxy.royaleapi.dev/v1/players/%23{clean_tag}/battlelog"
        headers = {"Authorization": f"Bearer {API_KEY}"}
        
        r = requests.get(url, headers=headers)
        if r.status_code != 200:
            print(f"Error fetching {tag}: {r.status_code}")
            continue

        new_battles = r.json()
        file_path = os.path.join(DATA_DIR, f"{clean_tag}.json")
        existing = []

        if os.path.exists(file_path):
            with open(file_path, "r") as f:
                try: existing = json.load(f)
                except: existing = []

        existing_times = {b['battleTime'] for b in existing}
        for battle in new_battles:
            if battle['battleTime'] not in existing_times:
                existing.append(battle)

        existing.sort(key=lambda x: x['battleTime'])
        with open(file_path, "w") as f:
            json.dump(existing, f, indent=4)

        # --- এনালাইসিস শুরু ---
        wins = losses = draws = 0
        units, cur_spells, cur_buildings = [], [], []
        streaks = []
        last_match = "Never"

        if existing:
            raw = existing[-1]['battleTime']
            dt = datetime.strptime(raw, '%Y%m%dT%H%M%S.%fZ')
            last_match = dt.strftime('%d %b %I:%M %p')

            for b in existing:
                my = b['team'][0]['crowns']
                op = b['opponent'][0]['crowns']
                for card in b['team'][0]['cards']:
                    name = card['name']
                    if name in SPELLS: cur_spells.append(name)
                    elif name in BUILDINGS: cur_buildings.append(name)
                    else: units.append(name)

                if my > op:
                    wins += 1; streaks.append('W')
                elif my < op:
                    losses += 1; streaks.append('L')
                else:
                    draws += 1; streaks.append('D')

        # স্ট্রিক ক্যালকুলেশন
        max_w = max_l = cur_w = cur_l = 0
        for s in streaks:
            if s == 'W': cur_w += 1; cur_l = 0; max_w = max(max_w, cur_w)
            elif s == 'L': cur_l += 1; cur_w = 0; max_l = max(max_l, cur_l)
            else: cur_w = cur_l = 0

        summary_data.append({
            "name": existing[-1]['team'][0]['name'] if existing else clean_tag,
            "total_matches": len(existing),
            "win_loss": f"{wins}W / {losses}L / {draws}D",
            "max_streaks": f"Win: {max_w}, Loss: {max_l}",
            "top_units": ", ".join([x[0] for x in Counter(units).most_common(5)]),
            "top_spells": ", ".join([x[0] for x in Counter(cur_spells).most_common(3)]),
            "last_match": last_match
        })

    with open(os.path.join(DATA_DIR, "summary.json"), "w") as f:
        json.dump(summary_data, f, indent=4)

if __name__ == "__main__":
    fetch_and_save()
