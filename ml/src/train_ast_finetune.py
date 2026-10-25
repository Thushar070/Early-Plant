import os
import csv
import numpy as np
import pandas as pd
import librosa
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from transformers import AutoProcessor, ASTModel
from sklearn.metrics import accuracy_score, f1_score
from config import SEED
from reproducibility import seed_everything

seed_everything(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_name = "MIT/ast-finetuned-audioset-10-10-0.4593"

epochs = 30
batch_size = 8
base_lr = 1e-5
head_lr = 1e-3
patience = 7

latest_path = "ml/checkpoints/ast_finetune/latest.pt"
best_path = "ml/checkpoints/ast_finetune/best.pt"
history_path = "ml/outputs/ast_finetune/training_history.csv"

os.makedirs("ml/checkpoints/ast_finetune", exist_ok=True)
os.makedirs("ml/outputs/ast_finetune", exist_ok=True)

processor = AutoProcessor.from_pretrained(model_name)
ast = ASTModel.from_pretrained(model_name).to(device)

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

        input_values = inputs["input_values"].squeeze(0)
        label = torch.tensor(
            int(row["label_id"]),
            dtype=torch.long
        )

        return input_values, label

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

for param in ast.parameters():
    param.requires_grad = False

for layer in ast.layers[-3:]:
    for param in layer.parameters():
        param.requires_grad = True

for param in ast.layernorm.parameters():
    param.requires_grad = True

model = ASTClassifier(ast).to(device)

base_params = []
head_params = list(model.head.parameters())

for name, param in model.ast.named_parameters():
    if param.requires_grad:
        base_params.append(param)

optimizer = torch.optim.AdamW(
    [
        {"params": base_params, "lr": base_lr},
        {"params": head_params, "lr": head_lr}
    ],
    weight_decay=1e-4
)

criterion = nn.CrossEntropyLoss()

train_dataset = PlantDataset("train.csv")
val_dataset = PlantDataset("val.csv")

train_loader = DataLoader(
    train_dataset,
    batch_size=batch_size,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_dataset,
    batch_size=batch_size,
    shuffle=False,
    num_workers=0
)

start_epoch = 0
best_f1 = 0.0
bad_epochs = 0

if os.path.exists(latest_path):
    checkpoint = torch.load(
        latest_path,
        map_location=device
    )

    model.load_state_dict(
        checkpoint["model_state"]
    )

    optimizer.load_state_dict(
        checkpoint["optimizer_state"]
    )

    start_epoch = checkpoint["epoch"] + 1
    best_f1 = checkpoint["best_f1"]
    bad_epochs = checkpoint["bad_epochs"]

    print(f"Resuming from epoch {start_epoch + 1}")
    print(f"Best validation Macro F1: {best_f1:.4f}")

if not os.path.exists(history_path):
    with open(history_path, "w", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            "epoch",
            "train_loss",
            "val_loss",
            "val_accuracy",
            "val_macro_f1"
        ])

for epoch in range(start_epoch, epochs):
    model.train()

    train_loss = 0.0

    for audio, labels in train_loader:
        audio = audio.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        outputs = model(audio)

        loss = criterion(
            outputs,
            labels
        )

        loss.backward()

        torch.nn.utils.clip_grad_norm_(
            model.parameters(),
            1.0
        )

        optimizer.step()

        train_loss += loss.item() * audio.size(0)

    train_loss /= len(train_loader.dataset)

    model.eval()

    val_loss = 0.0
    predictions = []
    targets = []

    with torch.no_grad():
        for audio, labels in val_loader:
            audio = audio.to(device)
            labels = labels.to(device)

            outputs = model(audio)

            loss = criterion(
                outputs,
                labels
            )

            val_loss += loss.item() * audio.size(0)

            preds = outputs.argmax(dim=1)

            predictions.extend(
                preds.cpu().tolist()
            )

            targets.extend(
                labels.cpu().tolist()
            )

    val_loss /= len(val_loader.dataset)

    val_accuracy = accuracy_score(
        targets,
        predictions
    )

    val_f1 = f1_score(
        targets,
        predictions,
        average="macro",
        zero_division=0
    )

    print(
        f"Epoch {epoch + 1}/{epochs} | "
        f"Train Loss: {train_loss:.4f} | "
        f"Val Loss: {val_loss:.4f} | "
        f"Val Accuracy: {val_accuracy:.4f} | "
        f"Val Macro F1: {val_f1:.4f}"
    )

    with open(history_path, "a", newline="") as f:
        writer = csv.writer(f)

        writer.writerow([
            epoch + 1,
            train_loss,
            val_loss,
            val_accuracy,
            val_f1
        ])

    checkpoint = {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "best_f1": best_f1,
        "bad_epochs": bad_epochs
    }

    torch.save(
        checkpoint,
        latest_path
    )

    if val_f1 > best_f1:
        best_f1 = val_f1
        bad_epochs = 0

        checkpoint["best_f1"] = best_f1
        checkpoint["bad_epochs"] = bad_epochs

        torch.save(
            checkpoint,
            best_path
        )

        print(
            f"Best checkpoint saved with Macro F1: {best_f1:.4f}"
        )
    else:
        bad_epochs += 1

    if bad_epochs >= patience:
        print("Early stopping")
        break

print("AST fine-tuning complete")
print(f"Best checkpoint: {best_path}")
print(f"Latest checkpoint: {latest_path}")
