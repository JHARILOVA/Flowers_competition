import os
import io
import sys
import json
import pandas as pd
from sklearn.metrics import f1_score, accuracy_score
def update_readme():
    if not os.path.exists('scores.json') or not os.path.exists('README.md'):
        return
        
    with open('scores.json', 'r') as f:
        scores = json.load(f)
    
    # Génération du tableau Markdown
    table = "| Rank | User | F1-Macro | Accuracy |\n| :--- | :--- | :--- | :--- |\n"
    for i, s in enumerate(scores, 1):
        table += f"| {i} | {s['user']} | {s['f1_macro']} | {s['accuracy']} |\n"
    
    with open('README.md', 'r') as f:
        content = f.read()

    # Délimiteurs pour isoler le tableau
    start_marker = "## 🏆 Leaderboard"
    end_marker = "📁 **Repository Structure**"

    if start_marker in content and end_marker in content:
        parts_before = content.split(start_marker)[0]
        parts_after = content.split(end_marker)[1]
        
        # On reconstruit le README en insérant le tableau entre les deux
        new_readme = parts_before + start_marker + "\n\n" + table + "\n\n" + end_marker + parts_after
        
        with open('README.md', 'w') as f:
            f.write(new_readme)
        print("README updated successfully!")
def update_leaderboard(username, f1, acc):
    """Updates the JSON database and sorts by performance."""
    scores_file = 'scores.json'
    if os.path.exists(scores_file):
        with open(scores_file, 'r') as f:
            scores = json.load(f)
    else:
        scores = []

    # Remove old score for this user if it exists to allow re-submissions
    scores = [s for s in scores if s['user'] != username]
    
    # Append new score
    scores.append({
        "user": username, 
        "f1_macro": round(f1, 4), 
        "accuracy": round(acc, 4)
    })
    
    # Sort by F1 descending (Highest first)
    scores = sorted(scores, key=lambda x: x['f1_macro'], reverse=True)

    with open(scores_file, 'w') as f:
        json.dump(scores, f, indent=4)

def run_grading(student_username):
    # 1. Load the Secret Master List
    secret_data = os.getenv("FLOWER_ANSWERS")
    if not secret_data:
        print("Error: Secret answer key (FLOWER_ANSWERS) missing.")
        sys.exit(1)
    
    truth_df = pd.read_csv(io.StringIO(secret_data), names=['original_filename', 'label'])
    truth_df['id'] = range(len(truth_df))

    # 2. Load Student Submission
    try:
        sub_df = pd.read_csv('submissions/submission.csv')
    except Exception as e:
        print(f"Error reading submission.csv: {e}")
        sys.exit(1)
# --- CORRECTION POUR LE MATCHING ---
    # On s'assure que tout est en texte pour éviter l'erreur de tout à l'heure
    truth_df['original_filename'] = truth_df['original_filename'].astype(str)
    
    # Si l'étudiant a mis les noms de fichiers dans la colonne 'id', 
    # on renomme sa colonne 'id' en 'original_filename'
    if 'id' in sub_df.columns and 'Image_' in str(sub_df['id'].iloc[0]):
        sub_df = sub_df.rename(columns={'id': 'original_filename'})
    
    sub_df['original_filename'] = sub_df['original_filename'].astype(str)

    # 3. Smart Matching Logic
    if 'original_filename' in sub_df.columns:

        merged = pd.merge(truth_df, sub_df, on='original_filename', suffixes=('_true', '_pred'))

        y_true = merged['label_true']

        y_pred = merged['label_pred']

    elif 'id' in sub_df.columns:

        merged = pd.merge(truth_df, sub_df, on='id', suffixes=('_true', '_pred'))

        y_true = merged['label_true']

        y_pred = merged['label_pred']

    elif 'label' in sub_df.columns:

        if len(sub_df) != len(truth_df):

            print("Error: Label-only submission length mismatch.")

            sys.exit(1)

        y_true = truth_df['label']

        y_pred = sub_df['label']

    else:

        print("Error: Submission must have 'original_filename', 'id', or 'label' columns.")

        sys.exit(1) 

    # 4. Calculate Metrics
    f1 = f1_score(y_true, y_pred, average='macro')
    acc = accuracy_score(y_true, y_pred)

    # 5. Update Database AND THEN update the README
    update_leaderboard(student_username, f1, acc)
    update_readme()

if __name__ == "__main__":
    # Get username from command line argument
    user_arg = sys.argv[1] if len(sys.argv) > 1 else "Unknown"
    run_grading(user_arg)
