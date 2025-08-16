import numpy as np
from collections import defaultdict
from audio_fingerprint.loader import AudioLoader
from audio_fingerprint.stft import STFT
from audio_fingerprint.mel_filterbank import MelFilterBank
from audio_fingerprint.peaks import PeakPicker
from audio_fingerprint.fingerprint import Fingerprinter
from audio_fingerprint.database import Database


class Recognizer:
    def __init__(self, db: Database) -> None:
        self.db = db

        self.loader = AudioLoader()
        self.stft = STFT(fft_size=2048)
        self.mel_fb = MelFilterBank(sr=44100, n_fft=2048)
        self.peak_picker = PeakPicker()
        self.fingerprinter = Fingerprinter()

    def recognize(self, filepath: str):
        # 1. Load audio from file
        audio, sr = self.loader.load(filepath)

        # 2. Apply STFT
        spec = self.stft.compute_stft(audio)

        # 3. Apply mel fileterbank 
        m = self.mel_fb.mel_filter_bank()
        
        # We need M @ P where P has shape (freq_bins, frames). So we use .T
        # (128, 1025) @ (1025, 351) -> (128, 351)
        mel_spec = np.dot(m, spec.T)

        # Apply log compression (log-mel spectrogram)
        mel_spec_db = 10 * np.log10(mel_spec + 1e-10)

        # 4. Apply peak peacker
        peaks = self.peak_picker.find_peaks(mel_spec_db)

        # 5. Apply fingerprinting
        fingerprints = self.fingerprinter.generate_fingerprints(peaks)

        # 6. Matching
        return self._match(fingerprints)
    
    def _match(self, fingerprints):
        db_data = self.db.get_all()
        match_scores = defaultdict(list)

        for h, t in fingerprints:
            for song_id, entries in db_data.items():
                for db_hash, db_offset in entries:
                    if db_hash == h:  # ✅ hash match
                        delta = db_offset - t
                        match_scores[song_id].append(delta)

        # Find best alignment
        best_song, best_score = None, 0
        for song_id, deltas in match_scores.items():
            if deltas:
                most_common = max(set(deltas), key=deltas.count)
                score = deltas.count(most_common)
                if score > best_score:
                    best_song, best_score = song_id, score

        return best_song, best_score