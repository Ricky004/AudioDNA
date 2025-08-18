from audio_fingerprint.fingerprint_extracter import FingerprintExtracter
from audio_fingerprint.database import Database


class UploadSong:
    def __init__(self, db: Database) -> None:
        self.db = db
        self.fingerprint_extracter = FingerprintExtracter()

    def upload_new_song(self, filepath: str, song_name: str, artist: str) -> int:
        # 1. Store metadata of the song
        self.db.add_song(song_name, artist)

        # 2. Fetch the song id
        song_id = self.db.get_song_id(song_name, artist)
        if not song_id:
            raise ValueError(f"Failed to retrieve song_id for {song_name} - {artist}")
        
        # 3. Generate fingerprints
        fingerprints = self.fingerprint_extracter.extract(filepath)
        if not fingerprints:
            raise ValueError("No fingerprints generated for file: " + filepath)
        
        # 4. Store fingerprints in the db
        self.db.add_fingerprints(fingerprints, song_id)

        return song_id

        
           