import os
import io
import sys
import json
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score

def run_grading(student_username):
    # 1. Load the Secret Master List (Always filename + label)
    secret_data = os.getenv("FLOWER_ANSWERS")
    if not secret_data:
        print("Error: Secret answer key missing.")
        sys.exit(1)
    
    # We load your secret and create a helper 'id' column based on row order
    truth_df = pd.read_csv(io.StringIO(secret_data), names=['original_filename', 'label'])
    truth_df['id'] = range(len(truth_df))

    # 2. Load Student Submission
    try:
        sub_df = pd.read_csv('submission.csv')
    except Exception as e:
        print(f"Error reading submission.csv: {e}")
        sys.exit(1)

    # 3. Smart Matching Logic
    # Scenario A: Filename and Label provided
    if 'original_filename' in sub_df.columns:
        merged = pd.merge(truth_df, sub_df, on='original_filename', suffixes=('_true', '_pred'))
        y_true = merged['label_true']
        y_pred = merged['label_pred']

    # Scenario B: ID and Label provided
    elif 'id' in sub_df.columns:
        merged = pd.merge(truth_df, sub_df, on='id', suffixes=('_true', '_pred'))
        y_true = merged['label_true']
        y_pred = merged['label_pred']

    # Scenario C: Only 'label' provided
    elif 'label' in sub_df.columns:
        if len(sub_df) != len(truth_df):
            print("Error: Label-only submission length does not match test set.")
            sys.exit(1)
        y_true = truth_df['label']
        y_pred = sub_df['label']
    
    else:
        print("Error: Submission must have 'original_filename', 'id', or at least 'label' column.")
        sys.exit(1)

    # 4. Calculate Metrics
    f1 = f1_score(y_true, y_pred, average='macro')
    acc = accuracy_score(y_true, y_pred)

    # 5. Update Database
    update_leaderboard(student_username, f1, acc)

def update_leaderboard(username, f1, acc):
    scores_file = 'scores.json'
    if os.path.exists(scores_file):
        with open(scores_file, 'r') as f:
            scores = json.load(f)
    else:
        scores = []

    # Update logic
    scores = [s for s in scores if s['user'] != username]
    scores.append({
        "user": username, 
        "f1_macro": round(f1, 4), 
        "accuracy": round(acc, 4)
    })
    
    # Sort by F1 descending
    scores = sorted(scores, key=lambda x: x['f1_macro'], reverse=True)

    with open(scores_file, 'w') as f:
        json.dump(scores, f, indent=4)

if __name__ == "__main__":
    user = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    run_grading(user)
