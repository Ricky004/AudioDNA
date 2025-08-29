from fastapi import APIRouter, HTTPException, Request
from server.service.spotify_service import audiodna_endpoint, add_song_to_db, SpotifyLink

router = APIRouter()

@router.post("/audiodna")
async def audio_recognizer(req: Request):
    try:
        return await audiodna_endpoint(req)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))

@router.post("/get-song-info")
def song_info(link: SpotifyLink):
    try:
        return add_song_to_db(link.url)
    except Exception as e:
        raise HTTPException(status_code=400, detail=str(e))
