import numpy as np
import logging
from scipy.ndimage import maximum_filter, median_filter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PeakPicker:
    def __init__(self, neighborhood_size=(15, 7), median_filter_size=(41, 21), offset_db=7.0, peaks_per_band=30, bands_split=6):
        """
        Finds spectral peaks in a log-mel spectrogram using an adaptive threshold.

        Args:
            neighborhood_size (tuple): The (freq_bins, time_frames) footprint for the
                                     local maximum filter. A point is a peak if it's the
                                     brightest in this neighborhood.
            median_filter_size (tuple): The (freq_bins, time_frames) footprint for the
                                        median filter used to estimate the local background noise.
                                        Should be larger than neighborhood_size.
            offset_db (float): A peak's amplitude in dB must be this much greater than the
                               local background (median) to be considered a peak.
            peaks_per_band (int): Max number of peaks to keep per frequency band region after detection.
            bands_split (int): How many horizontal frequency regions to split the spectrogram into
                               for distributing peaks.
        """
        if not all(s % 2 == 1 for s in neighborhood_size):
            logger.warning(f"neighborhood_size {neighborhood_size} should have odd dimensions for symmetry.")
        if not all(s % 2 == 1 for s in median_filter_size):
            logger.warning(f"median_filter_size {median_filter_size} should have odd dimensions for symmetry.")

        self.neighborhood_size = neighborhood_size
        self.median_filter_size = median_filter_size
        self.offset_db = offset_db
        self.peaks_per_band = peaks_per_band
        self.bands_split = bands_split

    def find_peaks(self, mel_log_spec):
        """
        Finds peaks in the given log-mel spectrogram.

        Args:
            mel_log_spec (np.ndarray): The input spectrogram (freq_bins, time_frames).

        Returns:
            np.ndarray: An array of peaks, with each row being [time_idx, freq_idx, amplitude_db].
                        Returns an empty array if no peaks are found.
        """
        try:
            logger.info(f"Running peak picking: neighborhood={self.neighborhood_size}, "
                        f"offset_db={self.offset_db}")

            if np.max(mel_log_spec) <= 0:
                logger.warning("Spectrogram has zero or negative energy, no peaks found.")
                return np.empty((0, 3))

            spec_db = mel_log_spec

            # 1. Find all local maxima (candidates)
            # A point is a local maximum if it is greater than all its neighbors.
            local_max = maximum_filter(spec_db, size=self.neighborhood_size, mode='constant') == spec_db

            # 2. Create an adaptive threshold using a median filter
            # This estimates the local background energy.
            background = median_filter(spec_db, size=self.median_filter_size, mode='constant')

            # 3. Apply the adaptive threshold
            # A peak must be a local maximum AND be significantly louder than its local background.
            detected_peaks = local_max & (spec_db > background + self.offset_db)

            # 4. Exclude edges to avoid artifacts from filtering
            mask = np.ones_like(spec_db, dtype=bool)
            f_half, t_half = self.neighborhood_size[0] // 2, self.neighborhood_size[1] // 2
            if f_half > 0:
                mask[:f_half, :] = False
                mask[-f_half:, :] = False
            if t_half > 0:
                mask[:, :t_half] = False
                mask[:, -t_half:] = False
            detected_peaks &= mask

            # 5. Collect peaks
            freq_idx, time_idx = np.nonzero(detected_peaks)
            amplitudes = spec_db[freq_idx, time_idx]
            peaks = np.column_stack((time_idx, freq_idx, amplitudes))

            if peaks.shape[0] == 0:
                logger.warning("No peaks found after filtering.")
                return np.empty((0, 3))

            # 6. Distribute peaks across frequency bands to ensure good coverage
            final_peaks = []
            total_freq_bins = mel_log_spec.shape[0]
            band_step = total_freq_bins // self.bands_split if self.bands_split > 0 else total_freq_bins

            for start in range(0, total_freq_bins, band_step):
                end = min(start + band_step, total_freq_bins)
                # Filter peaks that fall within the current frequency band
                band_peaks = peaks[(peaks[:, 1] >= start) & (peaks[:, 1] < end)]
                # Sort the peaks in this band by amplitude (descending)
                sorted_band_peaks = band_peaks[np.argsort(-band_peaks[:, 2])]
                # Keep only the top 'peaks_per_band'
                final_peaks.extend(sorted_band_peaks[:self.peaks_per_band])

            final_peaks = np.array(final_peaks)
            logger.info(f"Found {len(final_peaks)} peaks (distributed across {self.bands_split} bands)")
            return final_peaks

        except Exception as e:
            logger.error(f"Error in peak picking: {e}")
            raise