import json
import os
from collections import Counter

# কার্ডের ক্যাটাগরি
SPELLS = ["The Log", "Fireball", "Arrows", "Zap", "Rocket", "Lightning", "Earthquake", "Poison", "Graveyard", "Void", "Giant Snowball", "Barbarian Barrel", "Royal Delivery"]
BUILDINGS = ["Inferno Tower", "Tesla", "Cannon", "X-Bow", "Mortar", "Elixir Collector", "Goblin Cage", "Bomb Tower", "Furnace", "Goblin Drill", "Barbarian Hut"]

def analyze_data():
    current_dir = os.path.dirname(os.path.abspath(__file__))
    data_dir = os.path.join(current_dir, "Data")
    
    if not os.path.exists(data_dir):
        print(f"Error: '{data_dir}' folder ti paoya jayni!")
        return

    files = [f for f in os.listdir(data_dir) if f.endswith(".json")]
    if not files:
        print("Data folder e kono file nei. Age collector.py run korun.")
        return

    print("\n" + "★" * 55)
    print("  CLASH ROYALE ULTIMATE BATTLE REPORT  ")
    print("★" * 55)

    for filename in files:
        file_path = os.path.join(data_dir, filename)
        with open(file_path, "r", encoding="utf-8") as f:
            try:
                battles = json.load(f)
            except: continue
            
        if not battles: continue
        
        p_name = battles[0]['team'][0].get('name', 'Unknown')
        p_tag = filename.replace(".json", "")
        
        print(f"\n>>> PLAYER: {p_name} (#{p_tag})")
        print("-" * 65)

        wins, losses, draws = 0, 0, 0
        opponents, win_ops, loss_ops, draw_ops = [], [], [], []
        all_cards = {"Normal": [], "Spell": [], "Building": []}
        decks, streaks = [], []

        for b in battles:
            my_c = b['team'][0].get('crowns', 0)
            op_c = b['opponent'][0].get('crowns', 0)
            op_name = b['opponent'][0].get('name', 'Unknown')
            op_tag = b['opponent'][0].get('tag', 'N/A')
            op_info = f"{op_name} ({op_tag})"
            
            opponents.append(op_info)
            
            curr_deck = sorted([c['name'] for c in b['team'][0]['cards']])
            if len(curr_deck) == 8:
                decks.append(tuple(curr_deck))
            
            for cn in curr_deck:
                if cn in SPELLS: all_cards["Spell"].append(cn)
                elif cn in BUILDINGS: all_cards["Building"].append(cn)
                else: all_cards["Normal"].append(cn)

            if my_c > op_c:
                wins += 1; win_ops.append(op_info); streaks.append('W')
            elif my_c < op_c:
                losses += 1; loss_ops.append(op_info); streaks.append('L')
            else:
                draws += 1; draw_ops.append(op_info); streaks.append('D')

        # ১. সামারি
        total = len(battles)
        wr = (wins/total*100) if total > 0 else 0
        print(f"[1] MATCH SUMMARY:")
        print(f"Total: {total} | Win: {wins} | Loss: {losses} | Draw: {draws} | WinRate: {wr:.1f}%")

        # ২. প্রতিপক্ষ বিশ্লেষণ (নাম + ট্যাগ + কত বার)
        print(f"\n[2] OPPONENT ANALYSIS:")
        if opponents:
            m_op = Counter(opponents).most_common(1)[0]
            print(f"Most Played vs  : {m_op[0]} -> {m_op[1]} bar")
        if win_ops:
            m_w = Counter(win_ops).most_common(1)[0]
            print(f"Most Wins vs    : {m_w[0]} -> {m_w[1]} bar")
        if loss_ops:
            m_l = Counter(loss_ops).most_common(1)[0]
            print(f"Most Lost vs    : {m_l[0]} -> {m_l[1]} bar")
        if draw_ops:
            m_d = Counter(draw_ops).most_common(1)[0]
            print(f"Most Draws vs   : {m_d[0]} -> {m_d[1]} bar")

        # ৩. স্ট্রিক (Win/Loss Streak)
        max_w, max_l, cur_w, cur_l = 0, 0, 0, 0
        for s in streaks:
            if s == 'W':
                cur_w += 1; cur_l = 0; max_w = max(max_w, cur_w)
            elif s == 'L':
                cur_l += 1; cur_w = 0; max_l = max(max_l, cur_l)
            else:
                cur_w = 0; cur_l = 0
        print(f"\n[3] STREAKS:")
        print(f"Highest Win Streak: {max_w} | Highest Loss Streak: {max_l}")

        # ৪. টপ ৫ কার্ড (ক্যাটাগরি অনুযায়ী)
        print(f"\n[4] TOP 5 CARDS BY CATEGORY:")
        for k, v in all_cards.items():
            t5 = Counter(v).most_common(5)
            print(f"  {k:<8}: " + ", ".join([f"{n}({c})" for n, c in t5]))

        # ৫. টপ ৪ ডেক (৮টি কার্ডসহ)
        print(f"\n[5] TOP 4 DECKS (All 8 Cards):")
        t_decks = Counter(decks).most_common(4)
        for i, (dk, ct) in enumerate(t_decks, 1):
            print(f"  {i}. Used {ct} times: [{', '.join(dk)}]")

    print("\n" + "=" * 55)
    input("Report sesh. Bondho korte Enter chapun...")

if __name__ == "__main__":
    analyze_data()