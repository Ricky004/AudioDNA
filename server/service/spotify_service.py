import os
import re
import spotipy
import yt_dlp
from fastapi import HTTPException
from spotipy.oauth2 import SpotifyClientCredentials 
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from audio_fingerprint.database import Database
from audio_fingerprint.song_uploader import UploadSong


class SpotifyLink(BaseModel):
    url: str 

class Settings(BaseSettings):
    client_id: str 
    client_secret: str
    
    model_config = SettingsConfigDict(
            env_file="server/.env",
            extra="ignore",
            case_sensitive=False
        )

settings = Settings()  # type: ignore

sp = spotipy.Spotify(
    auth_manager=SpotifyClientCredentials(
        client_id=settings.client_id,
        client_secret=settings.client_secret,
    )
)

def add_song_to_db(link: str):
    try:
        track = sp.track(link)
        if not track:
            raise HTTPException(status_code=404, detail="Track not found or invalid Spotify URL")
        
        db = Database()

        song_name = track.get("name")
        artists = [artist["name"] for artist in track.get("artists", [])]

        artists_str = ", ".join(artists)

        query = f"{song_name} {artists_str}"

        filename = f"{sanitize_filename(artists_str)} - {sanitize_filename(song_name)}"
        filepath = os.path.join("downloads", filename)

        final_filepath = download_song_from_yt(query, output_path=filepath)

        upload = UploadSong(db)
        upload.upload_new_song(final_filepath, song_name, artists)

        return {"status": "ok", "song": song_name, "artists": artists}

    except Exception as e:
        print("Error in add_song_to_db:", e)  # <-- debug log
        raise HTTPException(status_code=400, detail=str(e))

def sanitize_filename(name: str):
    # Remove invalid characters for Windows/Linux/macOS
    return re.sub(r'[\\/*?:"<>|]', "", name)

def download_song_from_yt(query: str, output_path="downloads/%(title)s.%(ext)s") -> str:
    ydl_opts = {
        'format': 'bestaudio/best',
        'outtmpl': output_path,
        'postprocessors': [
            {
                'key': 'FFmpegExtractAudio',  
                'preferredcodec': 'mp3',     
                'preferredquality': '192',    
            }
        ],
        'noplaylist': True,
    }
    with yt_dlp.YoutubeDL(ydl_opts) as ydl:
        # ytsearch1: limits to first search result
        ydl.download([f"ytsearch1:{query}"])

    final_path = output_path + ".mp3"
    return final_path