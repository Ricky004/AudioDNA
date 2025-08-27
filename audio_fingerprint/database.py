import json
import sqlite3
from typing import List, Tuple, Dict

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
                name TEXT NOT NULL,
                artists TEXT NOT NULL
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

    def add_song(self, song_name: str, artists: list):
        self.cursor = self._execute("INSERT INTO songs (name, artists) VALUES (?, ?)", (song_name, json.dumps(artists)))
    
    def add_fingerprints(self, fingerprints: List[Tuple[str, int]], song_id: int):
        data = [(h, song_id, t) for h, t in fingerprints]
        self._executemany("INSERT INTO fingerprints (hash, song_id, anchor_time) VALUES (?, ?, ?)", data)

    def get_song_id(self, name: str, artists: list) -> int:
        self.cursor = self._execute(
           "SELECT song_id FROM songs WHERE name = ? AND artists = ?",
           (name, artists),
        )
        row = self.cursor.fetchone()
        return row[0]


    def get_all_fingerprint(self):
        """Fetch all data from the fingerprints table."""
        self.cursor = self._execute("SELECT * FROM fingerprints")
        rows = self.cursor.fetchall()
    
        db_data = {}
        for song_id, h, offset in rows:
          if song_id not in db_data:
            db_data[song_id] = []
          db_data[song_id].append((h, offset))

        return db_data
    
    def get_all_songs(self):
        """Fetch all data from the fingerprints table."""
        self.cursor = self._execute("SELECT * FROM songs")
        rows = self.cursor.fetchall()
    
        db_data = {}
        for song_id, h, offset in rows:
          if song_id not in db_data:
            db_data[song_id] = []
          db_data[song_id].append((h, offset))

        return db_data  

    def find_matches(self, query_hashes: List[str]) -> Dict[int, Dict[str, List[int]]] | None:
        if not query_hashes:
            return None

        placeholders = ",".join("?" for _ in query_hashes)
        sql = f"""
            SELECT hash, song_id, anchor_time
            FROM fingerprints
            WHERE hash IN ({placeholders})
        """
        self.cursor = self._execute(sql, query_hashes)
        results = self.cursor.fetchall()

        if not results:
            return None

        matches: Dict[int, Dict[str, List[int]]] = {}

        for hash_val, song_id, anchor_time in results:
            if song_id not in matches:
                matches[song_id] = {}
            if hash_val not in matches[song_id]:
                matches[song_id][hash_val] = []
            matches[song_id][hash_val].append(anchor_time)

        return matches

    def clear(self):
        self._execute("DROP TABLE IF EXISTS fingerprints;")
        self._execute("DROP TABLE IF EXISTS songs;")
        self._create_tables()