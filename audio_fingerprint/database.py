import sqlite3
from typing import List, Tuple, Dict
from typing import Optional

class Database:
    def __init__(self, db_name="music.db"):
        self.db_name = db_name
        self.conn = sqlite3.connect(db_name)
        self.cursor = self.conn.cursor()
        self._create_tables()

    def _execute(self, query, params=None):
        if params:
            self.cursor.execute(query, params)
        else:
            self.cursor.execute(query)
        self.conn.commit()
        return self.cursor


    def _executemany(self, query, data):
        self.cursor.executemany(query, data)
        self.conn.commit()
        return self.cursor


    def _create_tables(self):
        self._execute("""
            CREATE TABLE IF NOT EXISTS songs (
                song_id INTEGER PRIMARY KEY AUTOINCREMENT,
                name TEXT NOT NULL UNIQUE,
                artist TEXT NOT NULL
            );
        """)
        self._execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                hash TEXT NOT NULL,
                song_id INTEGER NOT NULL,
                anchor_time INTEGER NOT NULL,
                FOREIGN KEY(song_id) REFERENCES songs(song_id)
            );
        """)
        self._execute("CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints (hash);")

    def add_song(self, song_name: str, artist: str):
        self.cursor = self._execute("INSERT INTO songs (name, artist) VALUES (?, ?)", (song_name, artist))
    
    def add_fingerprints(self, fingerprints: List[Tuple[str, int]], song_id: int):
        data = [(h, song_id, t) for h, t in fingerprints]
        self._executemany("INSERT INTO fingerprints (hash, song_id, anchor_time) VALUES (?, ?, ?)", data)

    def get_song_id(self, name: str, artist: str) -> int:
        self.cursor = self._execute(
           "SELECT song_id FROM songs WHERE name = ? AND artist = ?",
           (name, artist),
        )
        row = self.cursor.fetchone()
        return row[0]


    def get_all(self):
        """Fetch all data from the fingerprints table."""
        self.cursor = self._execute("SELECT * FROM fingerprints")
        rows = self.cursor.fetchall()
    
        db_data = {}
        for song_id, h, offset in rows:
          if song_id not in db_data:
            db_data[song_id] = []
          db_data[song_id].append((h, offset))

        return db_data

    def find_matches(self, query_hashes: List[str]) -> Dict[int, List[int]] | None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        pass

    def clear(self):
        self._execute("DROP TABLE IF EXISTS fingerprints;")
        self._execute("DROP TABLE IF EXISTS songs;")
        self._create_tables()