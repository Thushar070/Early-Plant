import os
import numpy as np
import pandas as pd
import librosa
import torch
from tqdm import tqdm
from panns_utils import load_audio_tagging

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")
output_dir = "ml/outputs/panns"
os.makedirs(output_dir, exist_ok=True)

model = load_audio_tagging(device)

def extract_embeddings(csv_path, output_name):
    data = pd.read_csv(csv_path)
    embeddings = []
    labels = []
    paths = []
    for _, row in tqdm(data.iterrows(), total=len(data), desc=output_name):
        audio, sr = librosa.load(row["audio_path"], sr=32000, mono=True)
        audio = np.expand_dims(audio, axis=0)
        _, embedding = model.inference(audio)
        embeddings.append(embedding[0])
        labels.append(int(row["label_id"]))
        paths.append(row["audio_path"])
    embeddings = np.asarray(embeddings, dtype=np.float32)
    labels = np.asarray(labels, dtype=np.int64)
    paths = np.asarray(paths)
    np.save(os.path.join(output_dir, f"{output_name}_embeddings.npy"), embeddings)
    np.save(os.path.join(output_dir, f"{output_name}_labels.npy"), labels)
    np.save(os.path.join(output_dir, f"{output_name}_paths.npy"), paths)
    print(f"{output_name} embeddings:", embeddings.shape)
    print(f"{output_name} labels:", labels.shape)

def main():
    extract_embeddings("train.csv", "train")
    extract_embeddings("val.csv", "val")
    extract_embeddings("test.csv", "test")
    print("PANNs embedding extraction complete")

if __name__ == "__main__":
    main()
