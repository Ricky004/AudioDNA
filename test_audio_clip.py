import librosa
import soundfile as sf

audio, sr = librosa.load("espresso.mp3", sr=44100, mono=True)
clip = audio[120*sr:130*sr]  

# Save as 16-bit PCM WAV
sf.write("song-4.wav", clip, sr, subtype='PCM_16')

