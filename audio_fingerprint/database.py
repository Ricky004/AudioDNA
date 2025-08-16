import sqlite3
from typing import List, Tuple, Dict

class Database:
    def __init__(self, db_name="fingerprints.db"):
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
                id INTEGER PRIMARY KEY,
                name TEXT NOT NULL UNIQUE
            );
        """)
        self._execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
                hash TEXT NOT NULL,
                song_id INTEGER NOT NULL,
                anchor_time INTEGER NOT NULL,
                FOREIGN KEY(song_id) REFERENCES songs(id)
            );
        """)
        self._execute("CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints (hash);")

    def add_song(self, song_name: str):
        self.cursor = self._execute("INSERT INTO songs (name) VALUES (?)", (song_name,))
        return self.cursor.lastrowid
    
    def add_fingerprints(self, fingerprints: List[Tuple[str, int]], song_id: int):
        data = [(h, song_id, t) for h, t in fingerprints]
        self._executemany("INSERT INTO fingerprints (hash, song_id, anchor_time) VALUES (?, ?, ?)", data)

    def find_matches(self, query_hashes: List[str]) -> Dict[int, List[int]] | None:
        conn = sqlite3.connect(self.db_name)
        cursor = conn.cursor()
        pass

    def get_song_name(self, song_id: int):
        pass

    def get_all(self):
        """Fetch all data from the fingerprints table."""
        self.cursor.execute("SELECT * FROM fingerprints")
        rows = self.cursor.fetchall()
    
        db_data = {}
        for song_id, h, offset in rows:
          if song_id not in db_data:
            db_data[song_id] = []
          db_data[song_id].append((h, offset))

        return db_data


    def clear(self):
        self._execute("DROP TABLE IF EXISTS fingerprints;")
        self._execute("DROP TABLE IF EXISTS songs;")
        self._create_tables()