import numpy as np
from numpy.lib import stride_tricks
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class STFT:
    """
    A class computing Short-Time Fourier Transform (STFT) from audio input.
    """
     
    def __init__(self, fft_size: int = 1024, hop_size: int = 512, window_type: str = "hann") -> None:
        """
        Initialize the STFT.
        """
        self.fft_size = fft_size
        self.hop_size = hop_size
        self.window_type = window_type
        
    def compute_stft(self, x) -> np.ndarray:
        """
        Compute the STFT of the signal x.
        Returns:
            np.ndarray: STFT magnitude spectrogram with shape (frames, freq_bins)
        """
        try:
            logger.info(f"Input signal shape: {len(x)}")

            # Select window
            if self.window_type == "hann":
                window = np.hanning(self.fft_size)
            elif self.window_type == "hamming":
                window = np.hamming(self.fft_size)
            else:
                window = np.ones(self.fft_size)

            logger.info(f"Using window type: {self.window_type}")

            # Frame the signal
            frames = stride_tricks.sliding_window_view(x, self.fft_size)[::self.hop_size]
            logger.info(f"Frames shape: {frames.shape}")

            # Apply window
            frame_windowed = frames * window

            # FFT
            spec = np.fft.rfft(frame_windowed, n=self.fft_size, axis=1)
            logger.info(f"Spectrum shape: {spec.shape}")

            return np.abs(spec) ** 2

        except Exception as e:
            logger.error(f"STFT computation failed: {e}", exc_info=True)
            raise
