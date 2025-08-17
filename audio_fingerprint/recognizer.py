import numpy as np
from collections import defaultdict
from audio_fingerprint.loader import AudioLoader
from audio_fingerprint.stft import STFT
from audio_fingerprint.mel_filterbank import MelFilterBank
from audio_fingerprint.peaks import PeakPicker
from audio_fingerprint.fingerprint import Fingerprinter
from audio_fingerprint.fingerprint_extracter import FingerprintExtracter
from audio_fingerprint.database import Database


class Recognizer:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.fingerprint_extracter = FingerprintExtracter()

    def recognize(self, filepath: str):
        fingerprints = self.fingerprint_extracter.extarct(filepath=filepath)
        
        return self._match(fingerprints)
    
    def _match(self, fingerprints):
        db_data = self.db.get_all()
        match_scores = defaultdict(list)

        for h, t in fingerprints:
            for song_id, entries in db_data.items():
                for db_hash, db_offset in entries:
                    if db_hash == h:  
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