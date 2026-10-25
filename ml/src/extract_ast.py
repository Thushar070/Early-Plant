import os
import numpy as np
import pandas as pd
import librosa
import torch
from tqdm import tqdm
from transformers import AutoProcessor, ASTModel

device = torch.device("cuda" if torch.cuda.is_available() else "cpu")

model_name = "MIT/ast-finetuned-audioset-10-10-0.4593"
output_dir = "ml/outputs/ast"

os.makedirs(output_dir, exist_ok=True)

processor = AutoProcessor.from_pretrained(model_name)
model = ASTModel.from_pretrained(model_name).to(device)
model.eval()

def extract_embeddings(csv_path, output_name):
    data = pd.read_csv(csv_path)
    embeddings = []
    labels = []
    paths = []

    for _, row in tqdm(
        data.iterrows(),
        total=len(data),
        desc=output_name
    ):
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

        inputs = {
            key: value.to(device)
            for key, value in inputs.items()
        }

        with torch.no_grad():
            output = model(**inputs)

        embedding = output.pooler_output[0].cpu().numpy()

        embeddings.append(embedding)
        labels.append(int(row["label_id"]))
        paths.append(row["audio_path"])

    embeddings = np.asarray(
        embeddings,
        dtype=np.float32
    )

    labels = np.asarray(
        labels,
        dtype=np.int64
    )

    paths = np.asarray(paths)

    np.save(
        os.path.join(
            output_dir,
            f"{output_name}_embeddings.npy"
        ),
        embeddings
    )

    np.save(
        os.path.join(
            output_dir,
            f"{output_name}_labels.npy"
        ),
        labels
    )

    np.save(
        os.path.join(
            output_dir,
            f"{output_name}_paths.npy"
        ),
        paths
    )

    print(f"{output_name} embeddings:", embeddings.shape)
    print(f"{output_name} labels:", labels.shape)

def main():
    extract_embeddings("train.csv", "train")
    extract_embeddings("val.csv", "val")
    extract_embeddings("test.csv", "test")
    print("AST embedding extraction complete")

if __name__ == "__main__":
    main()
