import numpy as np
import pandas as pd
import librosa
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report
from panns_utils import load_audio_tagging, unwrap_panns_model

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

classes = [
    "Drought",
    "Heat Stress",
    "Mechanical Damage",
    "Nutrient Deficiency",
    "Pest Infestation"
]

class PlantDataset(Dataset):
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        audio, sr = librosa.load(row["audio_path"], sr=32000, mono=True)
        audio = torch.tensor(audio, dtype=torch.float32)
        label = torch.tensor(row["label_id"], dtype=torch.long)
        return audio, label

class PlantPANNs(nn.Module):
    def __init__(self):
        super().__init__()
        base = unwrap_panns_model(load_audio_tagging(device))
        self.base = base
        self.base.fc_audioset = nn.Identity()
        self.head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(2048, 5)
        )

    def forward(self, x):
        output = self.base(x)
        embedding = output["embedding"]
        return self.head(embedding)

test_data = PlantDataset("test.csv")

test_loader = DataLoader(
    test_data,
    batch_size=8,
    shuffle=False,
    num_workers=0
)

model = PlantPANNs().to(device)

checkpoint = torch.load(
    "ml/checkpoints/panns_finetune/best.pt",
    map_location=device
)

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

precision = precision_score(
    targets,
    predictions,
    average="macro",
    zero_division=0
)

recall = recall_score(
    targets,
    predictions,
    average="macro",
    zero_division=0
)

f1 = f1_score(
    targets,
    predictions,
    average="macro",
    zero_division=0
)

matrix = confusion_matrix(targets, predictions)

print("\nPANNs Fine-Tuned Test Results")
print("=============================")
print(f"Test Accuracy: {accuracy:.4f}")
print(f"Macro Precision: {precision:.4f}")
print(f"Macro Recall: {recall:.4f}")
print(f"Macro F1: {f1:.4f}")

print("\nClassification Report")
print("=====================")
print(classification_report(
    targets,
    predictions,
    target_names=classes,
    digits=4,
    zero_division=0
))

print("Confusion Matrix")
print("================")
print(matrix)
