import audiofile as af
import numpy as np
import logging
from pathlib import Path
from typing import Tuple


logger = logging.getLogger(__name__)

class AudioLoader:
    """
    A class to handle loading and preprocessing of audio files.
    """
    
    def __init__(self, sr: float = 44100, mono: bool = True) -> None:
      """
      Initialize the AudioLoader.

      Args:
          sr (int): Target sample rate.
          mono (bool): Convert to mono if True.
      
      """
      self.sr = sr
      self.mono = mono

    def load(self, filepath: str | Path) -> Tuple[np.ndarray, int]:
        """
        Load an audio file and preprocess it.
        """
        filepath = Path(filepath)

        if not filepath.exists():
          logger.error(f"File not found: {filepath}")
          raise FileNotFoundError(f"Audio file not found: {filepath}")
       
        try:
          logger.info(f"Loading audio file: {filepath}")
          audio, sr = af.read(str(filepath))
        
          if audio.size == 0:
              logger.error("Loaded audio is empty")
              raise ValueError("Audio file containes no data")
          
          # Convert stereo to mono if required
          if self.mono and audio.ndim > 1:
                audio = np.mean(audio, axis=0)
          
          logger.info(f"Audio loaded successfully: {audio.shape[0]} samples at {sr} Hz")
          return audio, sr
       
        except Exception as e:
            logger.exception(f"Error loading audio file {filepath}: {e}")
            raise ValueError(f"Failed to load audio file {filepath}: {e}") from e