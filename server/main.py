import uuid
from fastapi import FastAPI, UploadFile, File
from fastapi.middleware.cors import CORSMiddleware
import uvicorn
import shutil
import os

from audio_fingerprint.database import Database
from audio_fingerprint.recognizer import Recognizer

app = FastAPI()

# Enable CORS so React frontend can call the API
app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"], 
    allow_credentials=True,
    allow_methods=["*"],
    allow_headers=["*"],
)

UPLOAD_DIR = "uploads"
os.makedirs(UPLOAD_DIR, exist_ok=True)

@app.post("/api/v1/audiodna")
async def audiodna_endpoint(file: UploadFile = File(...)):
    unique_name = f"{uuid.uuid4()}.webm"
    filepath = os.path.join(UPLOAD_DIR, unique_name)

    # Save uploaded chunk to disk
    with open(filepath, "wb") as buffer:
        shutil.copyfileobj(file.file, buffer)

    db = Database("fingerprints.db")
    recognizer = Recognizer(db)
    song_id, score = recognizer.recognize(filepath)

    try:
        song_id, score = recognizer.recognize(filepath)
        result = {
            "status": "ok",
            "song_id": song_id,
            "confidence": score,
        }
    except Exception as e:
        result = {"status": "error", "message": str(e)}

    return result

if __name__ == "__main__":
    uvicorn.run("server:app", host="0.0.0.0", port=5000, reload=True)
