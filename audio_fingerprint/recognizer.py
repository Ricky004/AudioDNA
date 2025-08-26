from collections import defaultdict
from typing import List, Tuple
from audio_fingerprint.fingerprint_extracter import FingerprintExtracter
from audio_fingerprint.database import Database
import numpy as np


class Recognizer:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.extracter = FingerprintExtracter()

    def recognize(self, audio: np.ndarray):
        fingerprints = self.extracter.from_pcm(audio)
        
        return self._match(fingerprints)

    def _match(self, fingerprints: List[Tuple[str, int]], tolerance_ms: int = 100):
        match_scores = defaultdict(int)

        # group query fingerprints by hash
        query_by_hash = defaultdict(list)
        for h, t in fingerprints:   
            query_by_hash[h].append(t)

        for h, query_times in query_by_hash.items():
            db_matches = self.db.find_matches([h])
            if not db_matches:
                continue

            for song_id, song_hashes in db_matches.items():
                if h not in song_hashes:
                    continue
                db_times = song_hashes[h]

                # compare gaps in query vs db
                for i in range(len(query_times)):
                    for j in range(i + 1, len(query_times)):
                        q_gap = abs(query_times[j] - query_times[i])

                        for m in range(len(db_times)):
                            for n in range(m + 1, len(db_times)):
                                db_gap = abs(db_times[n] - db_times[m])

                                if abs(q_gap - db_gap) <= tolerance_ms:
                                    match_scores[song_id] += 1

        # pick best
        best_song, best_score = None, 0
        for song_id, score in match_scores.items():
            if score > best_score:
                best_song, best_score = song_id, score

        return best_song, best_score





