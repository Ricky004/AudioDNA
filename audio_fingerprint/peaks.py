import numpy as np
import logging
from scipy.ndimage import maximum_filter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PeakPicker:
    def __init__(self, neighborhood_size=(20, 10), threshold=0.3):
        """
        neighborhood_size: tuple (freq_bins, time_bins) for local max search
        threshold: minimum amplitude (normalized) to keep as a peak
        """
        self.neighborhood_size = neighborhood_size
        self.threshold = threshold

    def find_peaks(self, mel_log_spec):
        """
        Find strong peaks in a mel-log spectrogram (constellation map style).
        mel_log_spec: 2D array (freq_bins x time_frames)
        Returns: ndarray of shape (n_peaks, 3) with [time_idx, freq_idx, amplitude]
        """
        try:
            logger.info(f"Running peak picking: neighborhood={self.neighborhood_size}, "
                        f"threshold={self.threshold}")

            max_val = np.max(mel_log_spec)
            if max_val == 0:
                logger.warning("Spectrogram has zero energy, no peaks found.")
                return np.empty((0, 3))

            spec_norm = mel_log_spec / (np.max(mel_log_spec, axis=1, keepdims=True) + 1e-6)
            local_max = maximum_filter(spec_norm, size=self.neighborhood_size) == spec_norm
            detected_peaks = (spec_norm >= self.threshold) & local_max

            # Exclude edges
            mask = np.ones_like(spec_norm, dtype=bool)
            f_half, t_half = self.neighborhood_size[0] // 2, self.neighborhood_size[1] // 2
            mask[:f_half, :] = False
            mask[-f_half:, :] = False
            mask[:, :t_half] = False
            mask[:, -t_half:] = False
            detected_peaks &= mask

            freq_idx, time_idx = np.nonzero(detected_peaks)
            peaks = np.column_stack((time_idx, freq_idx, mel_log_spec[freq_idx, time_idx]))

            logger.info(f"Found {len(peaks)} peaks")
            return peaks

        except Exception as e:
            logger.error(f"Error in peak picking: {e}")
            raise
