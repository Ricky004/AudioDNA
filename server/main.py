from fastapi import FastAPI
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import numpy as np
from fastapi import Request

from audio_fingerprint.database import Database
from audio_fingerprint.recognizer import Recognizer
from server.api.v1.routes import router

app = FastAPI()

# Enable CORS so React frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

@app.post("/api/v1/audiodna")
async def audiodna_endpoint(request: Request):
    try: 
        body = await request.body()

        pcm_data = np.frombuffer(body, dtype=np.int16)
        
        audio = pcm_data.astype(np.float32) / 32768.0

        db = Database()
        recognizer = Recognizer(db)
        
        song_id, score = recognizer.recognize(audio)
        return {
                "status": "ok",
                "song_id": song_id,
                "confidence": score,
            }
    
    except Exception as e:
        return {"status": "error", "message": str(e)}

app.include_router(router, prefix="/api/v1", tags=["Spotify"])

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
