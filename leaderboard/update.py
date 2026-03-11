import json
import os
from datetime import datetime

def update_leaderboard():
    # 1. Load scores safely
    try:
        with open('scores.json', 'r') as f:
            scores = json.load(f)
    except Exception as e:
        print(f"Error loading scores.json: {e}")
        return

    # 2. Sort by accuracy
    scores.sort(key=lambda x: float(x.get('accuracy', '0').strip('%')), reverse=True)

    # 3. Build Table
    table = "| Rank | Participant | Accuracy | F1 (macro) | Date |\n"
    table += "| :--- | :--- | :--- | :--- | :--- |\n"
    
    for i, entry in enumerate(scores):
        rank = "🥇" if i == 0 else str(i + 1)
        table += f"| {rank} | {entry.get('participant', 'N/A')} | {entry.get('accuracy', '0%')} | {entry.get('f1_macro', '0%')} | {entry.get('date', '-')} |\n"

    # 4. Write to File
    now = datetime.utcnow().strftime('%Y-%m-%d %H:%M UTC')
    content = f"# 🌻 Flowers Competition Leaderboard\n\n*Last updated: {now}*\n\n{table}"
    
    os.makedirs('leaderboard', exist_ok=True)
    with open('leaderboard/README.md', 'w') as f:
        f.write(content)
    print("Leaderboard updated successfully!")

if __name__ == "__main__":
    update_leaderboard()
