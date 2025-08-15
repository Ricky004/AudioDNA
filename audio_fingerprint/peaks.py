import numpy as np
import logging
from scipy.ndimage import maximum_filter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PeakPicker:
    def __init__(self, neighborhood_size=(20, 10), threshold=0.3, peaks_per_band=5):
        """
        neighborhood_size: tuple (freq_bins, time_bins) for local max search
        threshold: base minimum amplitude (normalized)
        peaks_per_band: number of peaks to keep per frequency band region
        """
        self.neighborhood_size = neighborhood_size
        self.threshold = threshold
        self.peaks_per_band = peaks_per_band

    def find_peaks(self, mel_log_spec):
        """
        Find strong peaks in a mel-log spectrogram (constellation map style).
        mel_log_spec: 2D array (freq_bins x time_frames)
        Returns: ndarray of shape (n_peaks, 3) with [time_idx, freq_idx, amplitude]
        """
        try:
            logger.info(f"Running peak picking: neighborhood={self.neighborhood_size}, "
                        f"threshold={self.threshold}")

            if np.max(mel_log_spec) == 0:
                logger.warning("Spectrogram has zero energy, no peaks found.")
                return np.empty((0, 3))

            # Normalize each band individually
            spec_norm = mel_log_spec / (np.max(mel_log_spec, axis=1, keepdims=True) + 1e-9)

            # Local maxima detection
            local_max = maximum_filter(spec_norm, size=self.neighborhood_size) == spec_norm

            # Adaptive threshold per band
            adaptive_thresh = (spec_norm.T >= (self.threshold * 
                                               np.median(spec_norm, axis=1))).T

            detected_peaks = local_max & adaptive_thresh

            # Exclude edges
            mask = np.ones_like(spec_norm, dtype=bool)
            f_half, t_half = self.neighborhood_size[0] // 2, self.neighborhood_size[1] // 2
            mask[:f_half, :] = False
            mask[-f_half:, :] = False
            mask[:, :t_half] = False
            mask[:, -t_half:] = False
            detected_peaks &= mask

            # Get peak indices
            freq_idx, time_idx = np.nonzero(detected_peaks)
            amplitudes = mel_log_spec[freq_idx, time_idx]

            peaks = np.column_stack((time_idx, freq_idx, amplitudes))

            # Ensure vertical distribution
            final_peaks = []
            total_bands = mel_log_spec.shape[0]
            band_step = total_bands // 3  # low/mid/high split
            for start in range(0, total_bands, band_step):
                band_peaks = peaks[(peaks[:, 1] >= start) & (peaks[:, 1] < start + band_step)]
                # Sort by amplitude and keep top N
                band_peaks = band_peaks[np.argsort(-band_peaks[:, 2])]
                final_peaks.extend(band_peaks[:self.peaks_per_band])

            final_peaks = np.array(final_peaks)
            logger.info(f"Found {len(final_peaks)} peaks (distributed across bands)")
            return final_peaks

        except Exception as e:
            logger.error(f"Error in peak picking: {e}")
            raise
