import numpy as np
from audio_fingerprint.loader import AudioLoader
from audio_fingerprint.recognizer import Recognizer
from audio_fingerprint.stft import STFT
from audio_fingerprint.mel_filterbank import MelFilterBank
from audio_fingerprint.peaks import PeakPicker
from audio_fingerprint.fingerprint import Fingerprinter # Import the Fingerprinter class
import matplotlib.pyplot as plt
from audio_fingerprint.database import Database 


db = Database("fingerprints.db")   # or whatever DB file you use
    
# 2. Initialize Recognizer
recognizer = Recognizer(db)
    
# 3. Run recognition on a test file
filepath = "song.mp3"  # <-- replace with real file
song_id, score = recognizer.recognize(filepath)

# 4. Print result
if song_id:
    print(f"✅ Match found: Song ID {song_id} with score {score}")
else:
    print("❌ No match found")

