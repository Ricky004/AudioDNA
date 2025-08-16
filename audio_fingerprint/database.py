import sqlite3
from typing import List, Tuple, Dict


class Database:
    def __init__(self, db_name: str="fingerprints.db") -> None:
        self.db_name = db_name
        self.conn = None

    def connect_db(self):
        """
        Connects to the SQLite database and returns connection.
        """
        conn = sqlite3.connect(self.db_name)
        return conn
    
    def create_tables(self):
        """
        Creates the necessary tables if they don't exist.
        """
        conn = self.connect_db()
        cursor = conn.cursor()

        cursor.execute("""
            CREATE TABLE IF NOT EXISTS songs (
            id INTEGER PRIMARY KEY,
            name TEXT NOT NULL UNIQUE
            );
        """)

          # Table to store the fingerprints
        cursor.execute("""
            CREATE TABLE IF NOT EXISTS fingerprints (
            hash TEXT NOT NULL,
            song_id INTEGER NOT NULL,
            anchor_time INTEGER NOT NULL,
            FOREIGN KEY(song_id) REFERENCES songs(id)
            );
        """)

        cursor.execute("CREATE INDEX IF NOT EXISTS idx_hash ON fingerprints (hash);")
    
        conn.commit()
        conn.close()

    def add_song(self, song_name: str) -> int | None:
        conn = self.connect_db()
        cursor = conn.cursor()
        try:
            cursor.execute("INSERT INTO songs (name) VALUES (?)", (song_name,))
            conn.commit()
            song_id = cursor.lastrowid
            return song_id
        except sqlite3.IntegrityError:
            # Song already exists, retrieve its ID
            cursor.execute("SELECT id FROM songs WHERE name = ?", (song_name,))
            song_id = cursor.fetchone()[0]
            return song_id
        finally:
                conn.close()