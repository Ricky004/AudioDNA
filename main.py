import numpy as np
from audio_fingerprint.loader import AudioLoader
from audio_fingerprint.stft import STFT
import matplotlib.pyplot as plt

loader = AudioLoader(sr=16000)
audio, sr = loader.load("song.mp3")

stft = STFT(hop_size=256)
x = stft.stft(audio)

# Magnitude and Phase
magnitude = np.abs(x)
phase = np.angle(x)

print(f"STFT shape: {x.shape}")

print(f"Audio shape: {audio.shape}, Sample rate: {sr}")

magnitude_db = 20 * np.log10(magnitude + 1e-10)

plt.figure(figsize=(10, 6))
plt.imshow(
    magnitude_db.T[:1024//4],  # show only positive freqs
    origin="lower",
    aspect="auto",
    cmap="magma"
)
plt.colorbar(label="dB")
plt.xlabel("Frames")
plt.ylabel("Frequency bin")
plt.title("Spectrogram (from scratch STFT)")
plt.show()