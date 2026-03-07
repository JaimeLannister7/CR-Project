import requests
import json
import os
from collections import Counter
from datetime import datetime

API_KEY = os.getenv("eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjJmZjZlNWM1LTU2ZjctNDgzZS1hYWRhLTg1NjJjMDQ5ODUxMyIsImlhdCI6MTc3Mjg5ODM5MSwic3ViIjoiZGV2ZWxvcGVyLzY4ODAxNjIxLWI4NjgtYjA1OC0zZTI5LWRhMDNhNGMzN2U0YiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMDMuMTcwLjE3My4zNCJdLCJ0eXBlIjoiY2xpZW50In1dfQ.hOwSm3noWEnhSrvZu1oh8EAL36b89xempAYIzOt9_-ypMbN30OFzRHrXlQVkuVFgu2CZ19K49F3YAX9HSTtXlg")

PLAYER_FILE = "players.txt"
DATA_DIR = "Data"

SPELLS = ["Zap","The Log","Fireball","Arrows","Rocket","Lightning","Poison","Freeze","Tornado","Earthquake","Barbarian Barrel","Giant Snowball","Royal Delivery","Void","Rage","Mirror","Clone","Graveyard","Heal Spirit"]

BUILDINGS = ["Cannon","Inferno Tower","Tesla","Elixir Collector","Goblin Cage","Bomb Tower","Mortar","X-Bow","Barbarian Hut","Goblin Hut","Furnace","Goblin Drill","Cannon Cart"]


def fetch_and_save():

    if not os.path.exists(DATA_DIR):
        os.makedirs(DATA_DIR)

    if not os.path.exists(PLAYER_FILE):
        return

    with open(PLAYER_FILE,"r") as f:
        tags=[line.strip() for line in f if line.strip()]

    summary_data=[]

    for tag in tags:

        clean_tag=tag.replace("#","")

        url=f"https://proxy.royaleapi.dev/v1/players/%23{clean_tag}/battlelog"

        headers={
            "Authorization":f"Bearer {API_KEY}"
        }

        r=requests.get(url,headers=headers)

        if r.status_code!=200:
            print("API error",clean_tag,r.status_code)
            continue

        new_battles=r.json()

        file_path=os.path.join(DATA_DIR,f"{clean_tag}.json")

        existing=[]

        if os.path.exists(file_path):
            with open(file_path) as f:
                existing=json.load(f)

        existing_times={b['battleTime'] for b in existing}

        for battle in new_battles:
            if battle['battleTime'] not in existing_times:
                existing.append(battle)

        existing.sort(key=lambda x:x['battleTime'])

        with open(file_path,"w") as f:
            json.dump(existing,f,indent=4)

        wins=losses=draws=0
        units=[]
        spells=[]
        buildings=[]

        last="Never"

        if existing:

            raw=existing[-1]['battleTime']

            dt=datetime.strptime(raw,'%Y%m%dT%H%M%S.%fZ')

            last=dt.strftime('%d %b %I:%M %p')

        for b in existing:

            my=b['team'][0]['crowns']
            op=b['opponent'][0]['crowns']

            for card in b['team'][0]['cards']:

                name=card['name']

                if name in SPELLS:
                    spells.append(name)

                elif name in BUILDINGS:
                    buildings.append(name)

                else:
                    units.append(name)

            if my>op:
                wins+=1

            elif my<op:
                losses+=1

            else:
                draws+=1

        def top(arr,n=5):

            c=Counter(arr).most_common(n)

            return ", ".join([x[0] for x in c])

        summary_data.append({

            "name":existing[-1]['team'][0]['name'] if existing else clean_tag,

            "total":len(existing),

            "win":wins,

            "loss":losses,

            "draw":draws,

            "top_units":top(units),

            "top_spells":top(spells),

            "top_buildings":top(buildings),

            "last_match":last

        })

    with open(os.path.join(DATA_DIR,"summary.json"),"w") as f:
        json.dump(summary_data,f,indent=4)


fetch_and_save()
