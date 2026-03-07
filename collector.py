import requests
import json
import os
import time
if not os.path.exists('Data'):
    os.makedirs('Data')
# আপনার দেওয়া API Key
API_KEY = "eyJ0eXAiOiJKV1QiLCJhbGciOiJIUzUxMiIsImtpZCI6IjI4YTMxOGY3LTAwMDAtYTFlYi03ZmExLTJjNzQzM2M2Y2NhNSJ9.eyJpc3MiOiJzdXBlcmNlbGwiLCJhdWQiOiJzdXBlcmNlbGw6Z2FtZWFwaSIsImp0aSI6IjlkNWE1NTQ5LWZhM2YtNDJiNS05YzM3LTdjZjYzOWQ4NGNlNSIsImlhdCI6MTc3MjgxNDcwNywic3ViIjoiZGV2ZWxvcGVyLzY4ODAxNjIxLWI4NjgtYjA1OC0zZTI5LWRhMDNhNGMzN2U0YiIsInNjb3BlcyI6WyJyb3lhbGUiXSwibGltaXRzIjpbeyJ0aWVyIjoiZGV2ZWxvcGVyL3NpbHZlciIsInR5cGUiOiJ0aHJvdHRsaW5nIn0seyJjaWRycyI6WyIxMDMuMTcwLjE3My4zNCJdLCJ0eXBlIjoiY2xpZW50In1dfQ.nfL5j_cVAJtnuIZwN0YoQtvUyrd0uBSYfpBwbl1bIvJ2rxFOEbTKZvraMWJQSZqJTRP7iOM3MSDloBW017nKtg"
HEADERS = {'Authorization': f'Bearer {API_KEY}'}

def get_battle_log(player_tag):
    url = f"https://api.clashroyale.com/v1/players/%23{player_tag.strip('#')}/battlelog"
    try:
        response = requests.get(url, headers=HEADERS)
        if response.status_code == 200:
            return response.json()
    except:
        pass
    return []

def collect_data():
    if not os.path.exists("players.txt"):
        print("Error: players.txt ফাইলটি পাওয়া যায়নি!")
        return
    
    if not os.path.exists("Data"):
        os.makedirs("Data")

    with open("players.txt", "r") as f:
        tags = [line.strip() for line in f if line.strip()]

    print("-" * 50)
    print(f"সব ধরণের ম্যাচ স্ক্যান করা হচ্ছে... (Ranked/Ladder/War/Friendly)")
    print("-" * 50)

    for tag in tags:
        tag = tag.strip('#').upper()
        print(f"Checking Player #{tag}...", end=" ", flush=True)
        
        battles = get_battle_log(tag)
        
        file_path = f"Data/{tag}.json"
        existing_data = []
        if os.path.exists(file_path):
            with open(file_path, "r", encoding="utf-8") as f:
                try:
                    existing_data = json.load(f)
                except: existing_data = []

        existing_ids = {b['battleTime'] for b in existing_data}
        new_matches = []

        for b in battles:
            # এখানে কোনো ফিল্টার নেই, সব ধরণের নতুন ম্যাচ নেওয়া হবে
            if b['battleTime'] not in existing_ids:
                new_matches.append(b)

        if new_matches:
            combined_data = existing_data + new_matches
            with open(file_path, "w", encoding="utf-8") as f:
                json.dump(combined_data, f, indent=4)
            print(f"DONE! {len(new_matches)} টি নতুন ম্যাচ পাওয়া গেছে।")
        else:
            print("নতুন কোনো ম্যাচ নেই।")
        
        time.sleep(0.5)

if __name__ == "__main__":
    collect_data()
    print("-" * 50)

