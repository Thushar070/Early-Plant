import torch
import torch.nn as nn
import pandas as pd
import librosa
from torch.utils.data import Dataset, DataLoader
from transformers import AutoProcessor, ASTModel
from sklearn.metrics import accuracy_score, precision_score, recall_score, f1_score, confusion_matrix, classification_report

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_name = "MIT/ast-finetuned-audioset-10-10-0.4593"

classes = [
    "Drought",
    "Heat Stress",
    "Mechanical Damage",
    "Nutrient Deficiency",
    "Pest Infestation"
]

processor = AutoProcessor.from_pretrained(model_name)
ast = ASTModel.from_pretrained(model_name).to(device)

for param in ast.parameters():
    param.requires_grad = False

for layer in ast.layers[-3:]:
    for param in layer.parameters():
        param.requires_grad = True

for param in ast.layernorm.parameters():
    param.requires_grad = True

class ASTClassifier(nn.Module):
    def __init__(self, ast_model):
        super().__init__()
        self.ast = ast_model
        self.head = nn.Sequential(
            nn.Linear(768, 256),
            nn.ReLU(),
            nn.Dropout(0.3),
            nn.Linear(256, 5)
        )

    def forward(self, x):
        output = self.ast(input_values=x)
        x = output.pooler_output
        return self.head(x)

class PlantDataset(Dataset):
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]

        audio, sr = librosa.load(
            row["audio_path"],
            sr=16000,
            mono=True
        )

        inputs = processor(
            audio,
            sampling_rate=16000,
            return_tensors="pt"
        )

        audio = inputs["input_values"].squeeze(0)
        label = torch.tensor(
            int(row["label_id"]),
            dtype=torch.long
        )

        return audio, label

model = ASTClassifier(ast).to(device)

checkpoint = torch.load(
    "ml/checkpoints/ast_finetune/best.pt",
    map_location=device
)

model.load_state_dict(
    checkpoint["model_state"]
)

model.eval()

test_dataset = PlantDataset("test.csv")

test_loader = DataLoader(
    test_dataset,
    batch_size=8,
    shuffle=False,
    num_workers=0
)

predictions = []
targets = []

with torch.no_grad():
    for audio, labels in test_loader:
        audio = audio.to(device)

        outputs = model(audio)

        preds = outputs.argmax(dim=1)

        predictions.extend(
            preds.cpu().tolist()
        )

        targets.extend(
            labels.tolist()
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

print("\nAST Fine-tuned Test Results")
print("============================")
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
