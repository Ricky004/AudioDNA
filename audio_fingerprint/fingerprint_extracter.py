from typing import List, Tuple
from audio_fingerprint.loader import AudioLoader
from audio_fingerprint.stft import STFT
from audio_fingerprint.mel_filterbank import MelFilterBank
from audio_fingerprint.peaks import PeakPicker
from audio_fingerprint.fingerprint import Fingerprinter
import numpy as np


class FingerprintExtracter:
    def __init__(self,) -> None:
        self.loader = AudioLoader(mono=True)
        self.stft = STFT(fft_size=2048)
        self.mel_fb = MelFilterBank(sr=44100, n_fft=2048)
        self.peak_picker = PeakPicker()
        self.fingerprinter = Fingerprinter()
    
    def from_file(self, filepath: str):
        """Load audio from file and extract fingerprint."""
        audio, _ = self.loader.load(filepath)
        return self._extract(audio)

    def from_pcm(self, pcm_array: np.ndarray):
        """Use already captured PCM data and extract fingerprint."""
        return self._extract(pcm_array)

    def _extract(self, audio: np.ndarray) -> List[Tuple[str, int]]:
        # 2. Apply STFT
        spec = self.stft.compute_stft(audio)

        # 3. Apply mel filterbank 
        m = self.mel_fb.mel_filter_bank()
        
        # We need M @ P where P has shape (freq_bins, frames). So we use .T
        # (128, 1025) @ (1025, 351) -> (128, 351)
        mel_spec = np.dot(m, spec.T)

        # Apply log compression (log-mel spectrogram)
        mel_spec_db = 10 * np.log10(mel_spec + 1e-10)

        # 4. Apply peak picker
        peaks = self.peak_picker.find_peaks(mel_spec_db)

        # 5. Apply fingerprinting
        fingerprints = self.fingerprinter.generate_fingerprints(peaks)

        return fingerprints