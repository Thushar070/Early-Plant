import torch
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from model import PlantCNN
from dataset import create_loader
from config import CLASSES

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
model_path = "ml/checkpoints/best.pt"

test_loader = create_loader("test.csv", batch_size=16, shuffle=False)

model = PlantCNN().to(device)
checkpoint = torch.load(model_path, map_location=device)
model.load_state_dict(checkpoint["model_state"])
model.eval()

predictions = []
targets = []

with torch.no_grad():
    for audio, labels in test_loader:
        audio = audio.to(device)
        outputs = model(audio)
        preds = outputs.argmax(dim=1)
        predictions.extend(preds.cpu().tolist())
        targets.extend(labels.tolist())

accuracy = accuracy_score(targets, predictions)
precision = precision_score(targets, predictions, average="macro", zero_division=0)
recall = recall_score(targets, predictions, average="macro", zero_division=0)
f1 = f1_score(targets, predictions, average="macro", zero_division=0)
matrix = confusion_matrix(targets, predictions)

print("\nBaseline CNN Test Results")
print("=========================")
print(f"Test Accuracy: {accuracy:.4f}")
print(f"Macro Precision: {precision:.4f}")
print(f"Macro Recall: {recall:.4f}")
print(f"Macro F1: {f1:.4f}")

print("\nClassification Report")
print("=====================")
print(classification_report(
    targets,
    predictions,
    target_names=CLASSES,
    digits=4,
    zero_division=0
))

print("Confusion Matrix")
print("================")
print(matrix)