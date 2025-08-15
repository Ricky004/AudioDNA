import numpy as np
from audio_fingerprint.loader import AudioLoader
from audio_fingerprint.stft import STFT
from audio_fingerprint.mel_filterbank import MelFilterBank
from audio_fingerprint.peaks import PeakPicker
from audio_fingerprint.fingerprint import Fingerprinter # Import the Fingerprinter class
import matplotlib.pyplot as plt

# -------------------------------
# Load and preprocess audio
# -------------------------------
loader = AudioLoader(sr=16000)
audio, sr = loader.load("song.mp3")

stft = STFT(fft_size=2048, hop_size=512)
# Your STFT function returns shape (frames, freq_bins)
X = stft.compute_stft(audio)

# Magnitude and phase
magnitude = np.abs(X)
phase = np.angle(X)

print(f"STFT shape (frames, freq_bins): {magnitude.shape}") # Should show (351, 1025) or similar
print(f"Audio shape: {audio.shape}, Sample rate: {sr}")

# -------------------------------
# Mel filter bank + log compression
# -------------------------------
n_fft = stft.fft_size
n_mels = 128
mel_fb = MelFilterBank(sr=sr, n_fft=n_fft, n_mels=n_mels)
M = mel_fb.mel_filter_bank() # Shape: (n_mels, freq_bins) -> (128, 1025)

# Convert to power spectrum
magnitude_power = magnitude ** 2 # Shape: (frames, freq_bins) -> (351, 1025)

# Apply mel filter bank - FINAL FIX: Transpose the power spectrogram
# We need M @ P where P has shape (freq_bins, frames). So we use .T
# (128, 1025) @ (1025, 351) -> (128, 351)
mel_spec = np.dot(M, magnitude_power.T)

# The resulting mel_spec now has the correct (n_mels, frames) shape
print(f"Mel Spectrogram shape (n_mels, frames): {mel_spec.shape}")

# Apply log compression (log-mel spectrogram)
mel_spec_db = 10 * np.log10(mel_spec + 1e-10)

# -------------------------------
# Peak picking
# -------------------------------
picker = PeakPicker(
    neighborhood_size=(15, 7),
    median_filter_size=(41, 21),
    offset_db=7.0,
    peaks_per_band=30
)

peaks = picker.find_peaks(mel_spec_db)

if peaks.size == 0:
    print("⚠ No peaks found.")
else:
    times = peaks[:, 0].astype(int)
    freqs = peaks[:, 1].astype(int)
    amps = peaks[:, 2]

    # -------------------------------
    # Generate fingerprints
    # -------------------------------
    fingerprinter = Fingerprinter()
    fingerprints = fingerprinter.generate_fingerprints(peaks)
    
    if len(fingerprints) > 0:
        print(f"\n✅ Generated {len(fingerprints)} fingerprints.")
        print("First 5 fingerprints:")
        for fp in fingerprints[:5]:
            print(f"Hash: {fp[0]}, Anchor Time: {fp[1]}")
    else:
        print("\n⚠ No fingerprints generated.")

    # -------------------------------
    # Plot constellation map
    # -------------------------------
    plt.figure(figsize=(10, 6))
    plt.imshow(
        mel_spec_db,
        origin="lower",
        aspect="auto",
        cmap="magma"
    )
    plt.scatter(times, freqs, s=12, edgecolor="black", facecolor="cyan", linewidth=0.5)
    plt.ylim(0, n_mels - 1)
    plt.title("Constellation Map")
    plt.xlabel("Frames")
    plt.ylabel("Mel band index")
    plt.colorbar(label="Amplitude (dB)")
    plt.show()