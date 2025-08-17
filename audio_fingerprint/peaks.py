import numpy as np
import logging
from scipy.ndimage import maximum_filter, median_filter

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class PeakPicker:
    def __init__(self, neighborhood_size=(15, 7), median_filter_size=(41, 21),
                 offset_db=7.0, peaks_per_band=30, bands_split=6, time_window=60,
                 max_peaks_per_second=35, sr=44100, hop_size=512):
        """
        Finds spectral peaks in a log-mel spectrogram using an adaptive threshold.

        Args:
            neighborhood_size (tuple): Local maximum filter footprint (freq_bins, time_frames).
            median_filter_size (tuple): Median filter footprint for background.
            offset_db (float): Peak must exceed background + offset_db.
            peaks_per_band (int): Max peaks per band+time window.
            bands_split (int): Number of frequency bands.
            time_window (int): Number of frames per time slice.
            max_peaks_per_second (int): Global cap of peaks per second.
            sr (int): Sample rate (for time conversion).
            hop_size (int): Hop size between STFT frames.
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
        self.time_window = time_window
        self.max_peaks_per_second = max_peaks_per_second
        self.sr = sr
        self.hop_size = hop_size

    def find_peaks(self, mel_log_spec):
        try:
            logger.info(f"Running peak picking: neighborhood={self.neighborhood_size}, "
                        f"offset_db={self.offset_db}, time_window={self.time_window}, "
                        f"max_peaks_per_second={self.max_peaks_per_second}")

            if np.max(mel_log_spec) <= 0:
                logger.warning("Spectrogram has zero or negative energy, no peaks found.")
                return np.empty((0, 3))

            spec_db = mel_log_spec

            # 1. Local maxima
            local_max = maximum_filter(spec_db, size=self.neighborhood_size, mode='constant') == spec_db

            # 2. Local background
            background = median_filter(spec_db, size=self.median_filter_size, mode='constant')

            # 3. Apply adaptive threshold
            detected_peaks = local_max & (spec_db > background + self.offset_db)

            # 4. Exclude edges
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

            # 6. Distribute across frequency bands + time windows
            final_peaks = []
            total_freq_bins = mel_log_spec.shape[0]
            band_step = total_freq_bins // self.bands_split if self.bands_split > 0 else total_freq_bins

            for start in range(0, total_freq_bins, band_step):
                end = min(start + band_step, total_freq_bins)
                band_peaks = peaks[(peaks[:, 1] >= start) & (peaks[:, 1] < end)]

                if band_peaks.shape[0] == 0:
                    continue

                max_time = int(np.max(band_peaks[:, 0])) + 1
                for t0 in range(0, max_time, self.time_window):
                    t1 = t0 + self.time_window
                    time_slice = band_peaks[(band_peaks[:, 0] >= t0) & (band_peaks[:, 0] < t1)]
                    if time_slice.shape[0] == 0:
                        continue

                    sorted_time_peaks = time_slice[np.argsort(-time_slice[:, 2])]
                    final_peaks.extend(sorted_time_peaks[:self.peaks_per_band])

            final_peaks = np.array(final_peaks)

            # 7. Apply per-second cap
            if final_peaks.shape[0] > 0:
                times_sec = final_peaks[:, 0] * (self.hop_size / self.sr)
                clipped = []
                for sec in np.unique(times_sec.astype(int)):
                    idxs = np.where(times_sec.astype(int) == sec)[0]
                    if len(idxs) > self.max_peaks_per_second:
                        # keep loudest N
                        idxs = idxs[np.argsort(-final_peaks[idxs, 2])[:self.max_peaks_per_second]]
                    clipped.extend(final_peaks[idxs])
                final_peaks = np.array(clipped)

            logger.info(f"Found {len(final_peaks)} peaks after band+time+per-second limiting")
            return final_peaks

        except Exception as e:
            logger.error(f"Error in peak picking: {e}")
            raise
