import torch
import torchaudio
import librosa
import numpy as np
from config import SAMPLE_RATE, AUDIO_DIR

N_MELS = 128
N_FFT = 2048
HOP_LENGTH = 512

def load_audio(path):
    audio, sr = librosa.load(path, sr=SAMPLE_RATE, mono=True)
    return audio

def audio_to_mel(audio):
    mel = librosa.feature.melspectrogram(
        y=audio,
        sr=SAMPLE_RATE,
        n_fft=N_FFT,
        hop_length=HOP_LENGTH,
        n_mels=N_MELS
    )
    mel = librosa.power_to_db(mel, ref=np.max)
    return mel

def prepare_audio(path):
    audio = load_audio(path)
    mel = audio_to_mel(audio)
    tensor = torch.tensor(mel, dtype=torch.float32)
    tensor = tensor.unsqueeze(0)
    return tensor

def main():
    path = str(AUDIO_DIR / "plant_stress_341.wav")
    tensor = prepare_audio(path)

    print("Audio preprocessing test")
    print("Tensor shape:", tensor.shape)
    print("Tensor dtype:", tensor.dtype)
    print("Minimum:", tensor.min().item())
    print("Maximum:", tensor.max().item())

if __name__ == "__main__":
    main()