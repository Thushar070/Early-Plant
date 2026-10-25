import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

classes = [
    "Drought",
    "Heat Stress",
    "Mechanical Damage",
    "Nutrient Deficiency",
    "Pest Infestation"
]

x = np.load("ml/outputs/ast/test_embeddings.npy")
y = np.load("ml/outputs/ast/test_labels.npy")

x = torch.tensor(x, dtype=torch.float32)
y = torch.tensor(y, dtype=torch.long)

data = TensorDataset(x, y)

loader = DataLoader(
    data,
    batch_size=32,
    shuffle=False
)

class ASTClassifier(nn.Module):
    def __init__(self):
        super().__init__()
        self.net = nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 5)
        )

    def forward(self, x):
        return self.net(x)

model = ASTClassifier().to(device)

checkpoint = torch.load(
    "ml/checkpoints/ast/best.pt",
    map_location=device
)

model.load_state_dict(
    checkpoint["model_state"]
)

model.eval()

predictions = []
targets = []

with torch.no_grad():
    for x, y in loader:
        x = x.to(device)

        outputs = model(x)

        preds = outputs.argmax(dim=1)

        predictions.extend(
            preds.cpu().tolist()
        )

        targets.extend(
            y.tolist()
        )

accuracy = accuracy_score(
    targets,
    predictions
)

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

matrix = confusion_matrix(
    targets,
    predictions
)

print("\nAST Frozen Test Results")
print("=======================")
print(f"Test Accuracy: {accuracy:.4f}")
print(f"Macro Precision: {precision:.4f}")
print(f"Macro Recall: {recall:.4f}")
print(f"Macro F1: {f1:.4f}")

print("\nClassification Report")
print("=====================")

print(
    classification_report(
        targets,
        predictions,
        target_names=classes,
        digits=4,
        zero_division=0
    )
)

print("Confusion Matrix")
print("================")

print(matrix)
