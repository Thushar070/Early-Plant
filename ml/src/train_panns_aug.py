import os
import csv
import numpy as np
import pandas as pd
import librosa
import torch
import torch.nn as nn
from torch.utils.data import Dataset, DataLoader
from sklearn.metrics import accuracy_score, f1_score
from config import SEED
from reproducibility import seed_everything
from panns_utils import load_audio_tagging, unwrap_panns_model

seed_everything(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

epochs = 30
batch_size = 8
lr_base = 1e-5
lr_head = 1e-3
patience = 7

class PlantDataset(Dataset):
    def __init__(self, csv_path, augment=False):
        self.data = pd.read_csv(csv_path)
        self.augment = augment

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        audio, sr = librosa.load(row["audio_path"], sr=32000, mono=True)
        audio = torch.tensor(audio, dtype=torch.float32)

        if self.augment:
            if torch.rand(1).item() < 0.5:
                audio = audio * torch.empty(1).uniform_(0.9, 1.1).item()

            if torch.rand(1).item() < 0.5:
                shift = int(torch.randint(-1600, 1601, (1,)).item())
                audio = torch.roll(audio, shift)

            if torch.rand(1).item() < 0.5:
                noise = torch.randn_like(audio) * 0.002
                audio = audio + noise

        label = torch.tensor(row["label_id"], dtype=torch.long)
        return audio, label

class PlantPANNs(nn.Module):
    def __init__(self):
        super().__init__()
        base = unwrap_panns_model(load_audio_tagging(device))
        self.base = base
        self.base.fc_audioset = nn.Identity()

        for p in self.base.parameters():
            p.requires_grad = False

        for p in self.base.conv_block5.parameters():
            p.requires_grad = True

        for p in self.base.conv_block6.parameters():
            p.requires_grad = True

        for p in self.base.fc1.parameters():
            p.requires_grad = True

        self.head = nn.Sequential(
            nn.Dropout(0.3),
            nn.Linear(2048, 5)
        )

    def forward(self, x):
        output = self.base(x)
        embedding = output["embedding"]
        return self.head(embedding)

train_data = PlantDataset("train.csv", augment=True)
val_data = PlantDataset("val.csv", augment=False)

train_loader = DataLoader(
    train_data,
    batch_size=batch_size,
    shuffle=True,
    num_workers=0
)

val_loader = DataLoader(
    val_data,
    batch_size=batch_size,
    shuffle=False,
    num_workers=0
)

model = PlantPANNs().to(device)

base_params = []
head_params = []

for name, param in model.named_parameters():
    if not param.requires_grad:
        continue

    if name.startswith("head"):
        head_params.append(param)
    else:
        base_params.append(param)

optimizer = torch.optim.AdamW(
    [
        {"params": base_params, "lr": lr_base},
        {"params": head_params, "lr": lr_head}
    ],
    weight_decay=1e-4
)

criterion = nn.CrossEntropyLoss()

latest_path = "ml/checkpoints/panns_aug/latest.pt"
best_path = "ml/checkpoints/panns_aug/best.pt"
history_path = "ml/outputs/panns_aug/training_history.csv"

os.makedirs("ml/checkpoints/panns_aug", exist_ok=True)
os.makedirs("ml/outputs/panns_aug", exist_ok=True)

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

    if val_f1 > best_f1:
        best_f1 = val_f1
        bad_epochs = 0

        checkpoint = {
            "epoch": epoch,
            "model_state": model.state_dict(),
            "optimizer_state": optimizer.state_dict(),
            "best_f1": best_f1,
            "bad_epochs": bad_epochs
        }

        torch.save(
            checkpoint,
            best_path
        )

        print(
            f"Best checkpoint saved with Macro F1: {best_f1:.4f}"
        )
    else:
        bad_epochs += 1

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

    if bad_epochs >= patience:
        print("Early stopping")
        break

print("PANNs augmentation training complete")
print(f"Best checkpoint: {best_path}")
print(f"Latest checkpoint: {latest_path}")
