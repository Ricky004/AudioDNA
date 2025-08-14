import numpy as np
from audio_fingerprint.loader import AudioLoader
from audio_fingerprint.stft import STFT
from audio_fingerprint.mel_filterbank import MelFilterBank
import matplotlib.pyplot as plt

loader = AudioLoader(sr=16000)
audio, sr = loader.load("song.mp3")

stft = STFT(hop_size=256)
x = stft.compute_stft(audio)


# Magnitude and Phase
magnitude = np.abs(x)
phase = np.angle(x)

print(f"STFT shape: {x.shape}")

print(f"Audio shape: {audio.shape}, Sample rate: {sr}")

n_fft = stft.fft_size
n_mels = 128
mel_fb = MelFilterBank(sr=sr, n_fft=n_fft, n_mels=n_mels)
m = mel_fb.mel_filter_bank()
magnitude_power = magnitude**2  # convert to power

# Apply mel filter bank
mel_spec = np.dot(m, magnitude_power.T).T  # shape: (frames, n_mels)

# Apply log compression
mel_spec_log = np.log1p(mel_spec)  # log(1 + x) to avoid log(0)

# Plot mel-log spectrogram
plt.figure(figsize=(10, 6))
plt.imshow(
    mel_spec_log.T,
    origin="lower",
    aspect="auto",
    cmap="magma",
    extent=(0, mel_spec_log.shape[0], 0, n_mels)
)
plt.colorbar(label="Log amplitude")
plt.xlabel("Frames")
plt.ylabel("Mel band")
plt.title("Mel-Log Spectrogram (from scratch STFT)")
plt.show()