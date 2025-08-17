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
        fingerprints = self.fingerprint_extracter.extract(filepath=filepath)
        
        return self._match(fingerprints)
    
    def _match(self, fingerprints):
        match_scores = defaultdict(list)

        for h, query_offset in fingerprints:
            db_matches = self.db.find_matches([h])  
            if not db_matches:
                continue

            for song_id, offsets in db_matches.items():
                for db_offset in offsets:
                    delta = db_offset - query_offset
                    match_scores[song_id].append(delta)

        best_song, best_score = None, 0
        for song_id, deltas in match_scores.items():
            if deltas:
                most_common = max(set(deltas), key=deltas.count)
                score = deltas.count(most_common)
                if score > best_score:
                    best_song, best_score = song_id, score

        # Confidence threshold
        if best_score < 20:
            return None, 0

        return best_song, best_score

