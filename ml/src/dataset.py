import pandas as pd
import torch
from torch.utils.data import Dataset, DataLoader
from preprocessing import prepare_audio
from config import validate_label_id

class PlantAudioDataset(Dataset):
    def __init__(self, csv_path):
        self.data = pd.read_csv(csv_path)

    def __len__(self):
        return len(self.data)

    def __getitem__(self, index):
        row = self.data.iloc[index]
        audio = prepare_audio(row["audio_path"])
        label = torch.tensor(validate_label_id(row["label_id"]), dtype=torch.long)
        return audio, label

def create_loader(csv_path, batch_size=16, shuffle=False):
    dataset = PlantAudioDataset(csv_path)
    loader = DataLoader(
        dataset,
        batch_size=batch_size,
        shuffle=shuffle,
        num_workers=0
    )
    return loader

def main():
    train_loader = create_loader("train.csv", batch_size=16, shuffle=True)
    audio, label = next(iter(train_loader))
    print("Dataset test")
    print("Audio batch shape:", audio.shape)
    print("Label batch shape:", label.shape)
    print("Labels:", label.tolist())

if __name__ == "__main__":
    main()
