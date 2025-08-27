import spotipy
from fastapi import HTTPException
from spotipy.oauth2 import SpotifyClientCredentials 
from pydantic import BaseModel
from pydantic_settings import BaseSettings, SettingsConfigDict
from audio_fingerprint.database import Database


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

        db.add_song(song_name, artists)
    
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
