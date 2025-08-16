import numpy as np
import logging

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class MelFilterBank:
    def __init__(self, sr: float, n_fft: int, n_mels: int=128, fmin: int=0, fmax=None) -> None:
        self.sr = sr
        self.n_fft = n_fft
        self.n_mels = n_mels
        self.fmin = fmin
        self.fmax = fmax
    
    @staticmethod
    def hz_to_mel(hz):
        """Convert frequency in Hz to Mel scale."""
        return 2595 * np.log10(1 + hz / 700.0)
    
    @staticmethod
    def mel_to_hz(mel):
        """Convert Mel scale back to Hz."""
        return 700 * (10**(mel / 2595.0) - 1)

    def mel_filter_bank(self):
        """Create a Mel filter bank."""
        try:
            if self.sr <= 0:
                raise ValueError("Sample rate must be positive")
            if self.n_fft <= 0:
                raise ValueError("FFT size must be positive")
            if self.n_mels <= 0:
                raise ValueError("Number of mel bands must be positive")

            if self.fmax is None:
                self.fmax = self.sr / 2

            if self.fmax > self.sr / 2:
                raise ValueError("fmax cannot exceed Nyquist frequency (sr/2)")

            logger.info(f"Creating mel filter bank: sr={self.sr}, n_fft={self.n_fft}, "
                        f"n_mels={self.n_mels}, fmin={self.fmin}, fmax={self.fmax}")

            # Hz -> Mel
            mel_min = self.hz_to_mel(self.fmin)
            mel_max = self.hz_to_mel(self.fmax)

            # Mel points -> Hz points
            mel_points = np.linspace(mel_min, mel_max, self.n_mels + 2)
            hz_points = self.mel_to_hz(mel_points)

            # Hz -> FFT bin indices
            bin_points = np.floor((self.n_fft + 1) * hz_points / self.sr).astype(int)

            # Build filters
            filters = np.zeros((self.n_mels, self.n_fft // 2 + 1))
            for m in range(1, self.n_mels + 1):
                f_m_minus = bin_points[m - 1]
                f_m = bin_points[m]
                f_m_plus = bin_points[m + 1]

                for k in range(f_m_minus, f_m):
                    filters[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
                for k in range(f_m, f_m_plus):
                    filters[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

            logger.info("Mel filter bank created successfully")
            return filters

        except Exception as e:
            logger.error(f"Error creating mel filter bank: {e}")
            raise
