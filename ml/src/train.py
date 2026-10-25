import os
import csv
import torch
import torch.nn as nn
from torch.amp import autocast, GradScaler
from sklearn.metrics import accuracy_score, f1_score
from model import PlantCNN
from dataset import create_loader
from config import SEED
from reproducibility import seed_everything
from training_utils import update_best_metric

seed_everything(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
epochs = 30
batch_size = 16
lr = 0.001

latest_path = "ml/checkpoints/latest.pt"
best_path = "ml/checkpoints/best.pt"
history_path = "ml/outputs/training_history.csv"

os.makedirs("ml/checkpoints", exist_ok=True)
os.makedirs("ml/outputs", exist_ok=True)

train_loader = create_loader("train.csv", batch_size=batch_size, shuffle=True)
val_loader = create_loader("val.csv", batch_size=batch_size, shuffle=False)

model = PlantCNN().to(device)
criterion = nn.CrossEntropyLoss()
optimizer = torch.optim.AdamW(model.parameters(), lr=lr, weight_decay=1e-4)
scaler = GradScaler("cuda", enabled=device.type == "cuda")

start_epoch = 0
best_f1 = 0.0

if os.path.exists(latest_path):
    checkpoint = torch.load(latest_path, map_location=device)
    model.load_state_dict(checkpoint["model_state"])
    optimizer.load_state_dict(checkpoint["optimizer_state"])
    scaler.load_state_dict(checkpoint["scaler_state"])
    start_epoch = checkpoint["epoch"] + 1
    best_f1 = checkpoint["best_f1"]
    print(f"Resuming from epoch {start_epoch + 1}")
    print(f"Best validation Macro F1: {best_f1:.4f}")

if not os.path.exists(history_path):
    with open(history_path, "w", newline="") as f:
        writer = csv.writer(f)
        writer.writerow(["epoch", "train_loss", "val_loss", "val_accuracy", "val_macro_f1"])

for epoch in range(start_epoch, epochs):
    model.train()
    train_loss = 0.0

    for audio, labels in train_loader:
        audio = audio.to(device)
        labels = labels.to(device)

        optimizer.zero_grad()

        with autocast(device_type=device.type, enabled=device.type == "cuda"):
            outputs = model(audio)
            loss = criterion(outputs, labels)

        scaler.scale(loss).backward()
        scaler.step(optimizer)
        scaler.update()

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

            with autocast(device_type=device.type, enabled=device.type == "cuda"):
                outputs = model(audio)
                loss = criterion(outputs, labels)

            val_loss += loss.item() * audio.size(0)

            preds = outputs.argmax(dim=1)
            predictions.extend(preds.cpu().tolist())
            targets.extend(labels.cpu().tolist())

    val_loss /= len(val_loader.dataset)
    val_accuracy = accuracy_score(targets, predictions)
    val_f1 = f1_score(targets, predictions, average="macro")

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

    is_best, best_f1 = update_best_metric(val_f1, best_f1)
    checkpoint = {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "scaler_state": scaler.state_dict(),
        "best_f1": best_f1
    }

    torch.save(checkpoint, latest_path)

    if is_best:
        torch.save(checkpoint, best_path)
        print(f"Best checkpoint saved with Macro F1: {best_f1:.4f}")

print("Training complete")
print(f"Best checkpoint: {best_path}")
print(f"Latest checkpoint: {latest_path}")
