from sklearn.metrics import f1_score, classification_report
import torch

def calculate_final_metrics(model, dataloader, device):
    """
    Calculates Accuracy and F1-Macro score.
    F1-Macro is essential for this competition to ensure
    all flower classes are predicted accurately.
    """
    model.eval()
    all_preds = []
    all_labels = []

    with torch.no_grad():
        for images, labels in dataloader:
            images, labels = images.to(device), labels.to(device)
            outputs = model(images)
            _, preds = torch.max(outputs, 1)
            
            all_preds.extend(preds.cpu().numpy())
            all_labels.extend(labels.cpu().numpy())

    # Calculate scores
    f1 = f1_score(all_labels, all_preds, average='macro')
    report = classification_report(all_labels, all_preds)
    
    return f1, report
