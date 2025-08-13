from audio_fingerprint.loader import AudioLoader

loader = AudioLoader()
audio, sr = loader.load("song.mp3")


print(f"Audio shape: {audio.shape}, Sample rate: {sr}")