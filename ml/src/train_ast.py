import os
import csv
import numpy as np
import torch
import torch.nn as nn
from torch.utils.data import TensorDataset, DataLoader
from sklearn.metrics import accuracy_score, f1_score
from config import SEED
from reproducibility import seed_everything
from training_utils import update_best_metric

seed_everything(SEED)
device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

epochs = 50
batch_size = 32
lr = 0.001

train_x = np.load("ml/outputs/ast/train_embeddings.npy")
train_y = np.load("ml/outputs/ast/train_labels.npy")
val_x = np.load("ml/outputs/ast/val_embeddings.npy")
val_y = np.load("ml/outputs/ast/val_labels.npy")

train_x = torch.tensor(train_x, dtype=torch.float32)
train_y = torch.tensor(train_y, dtype=torch.long)
val_x = torch.tensor(val_x, dtype=torch.float32)
val_y = torch.tensor(val_y, dtype=torch.long)

train_data = TensorDataset(train_x, train_y)
val_data = TensorDataset(val_x, val_y)

train_loader = DataLoader(
    train_data,
    batch_size=batch_size,
    shuffle=True
)

val_loader = DataLoader(
    val_data,
    batch_size=batch_size,
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

criterion = nn.CrossEntropyLoss()

optimizer = torch.optim.AdamW(
    model.parameters(),
    lr=lr,
    weight_decay=1e-4
)

latest_path = "ml/checkpoints/ast/latest.pt"
best_path = "ml/checkpoints/ast/best.pt"
history_path = "ml/outputs/ast/training_history.csv"

os.makedirs("ml/checkpoints/ast", exist_ok=True)

start_epoch = 0
best_f1 = 0.0

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

    for x, y in train_loader:
        x = x.to(device)
        y = y.to(device)

        optimizer.zero_grad()

        outputs = model(x)
        loss = criterion(outputs, y)

        loss.backward()
        optimizer.step()

        train_loss += loss.item() * x.size(0)

    train_loss /= len(train_loader.dataset)

    model.eval()

    val_loss = 0.0
    predictions = []
    targets = []

    with torch.no_grad():
        for x, y in val_loader:
            x = x.to(device)
            y = y.to(device)

            outputs = model(x)
            loss = criterion(outputs, y)

            val_loss += loss.item() * x.size(0)

            preds = outputs.argmax(dim=1)

            predictions.extend(
                preds.cpu().tolist()
            )

            targets.extend(
                y.cpu().tolist()
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

    is_best, best_f1 = update_best_metric(val_f1, best_f1)
    checkpoint = {
        "epoch": epoch,
        "model_state": model.state_dict(),
        "optimizer_state": optimizer.state_dict(),
        "best_f1": best_f1
    }

    torch.save(checkpoint, latest_path)

    if is_best:
        torch.save(
            checkpoint,
            best_path
        )

        print(
            f"Best checkpoint saved with Macro F1: {best_f1:.4f}"
        )

print("AST classifier training complete")
print(f"Best checkpoint: {best_path}")
print(f"Latest checkpoint: {latest_path}")
