from fastapi import APIRouter, HTTPException
from server.service.spotify_service import add_song_to_db, SpotifyLink

router = APIRouter()

@router.post("/get-song-info")
def song_info(link: SpotifyLink):
    print("Received URL:", link.url)
    try:
        return add_song_to_db(link.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
