import numpy as np
from audio_fingerprint.loader import AudioLoader
from audio_fingerprint.stft import STFT
from audio_fingerprint.mel_filterbank import MelFilterBank
from audio_fingerprint.peaks import PeakPicker
import matplotlib.pyplot as plt

loader = AudioLoader(sr=16000)
audio, sr = loader.load("song.mp3")

stft = STFT(fft_size=2048, hop_size=512)
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
mel_spec_log = 10 * np.log10(mel_spec + 1e-10)

# Plot mel-log spectrogram
picker = PeakPicker(threshold=0.3, neighborhood_size=(5, 5))
peaks = picker.find_peaks(mel_spec_log)

# Plot constellation map
times, freqs, amps = zip(*peaks)
times = np.array(times)
freqs = np.array(freqs)
freqs = np.clip(freqs, 0, n_mels - 1)
plt.figure(figsize=(10, 6))
plt.imshow(mel_spec_log.T, origin="lower", aspect="auto", cmap="magma")
plt.scatter(times, freqs, s=10, edgecolor="black", facecolor="cyan")
plt.ylim(0, n_mels - 1)  # ✅ force axis to match Mel bins
plt.title("Constellation Map")
plt.xlabel("Frames")
plt.ylabel("Mel band index")
plt.show()

