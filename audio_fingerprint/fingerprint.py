import logging
import numpy as np
import hashlib
from typing import List, Tuple

logger = logging.getLogger(__name__)
logging.basicConfig(level=logging.INFO)

class Fingerprinter:
    """
    Generates robust audio fingerprints from a list of spectral peaks.

    The fingerprinting process is based on the Shazam algorithm's concept of
    creating hashes from pairs of peaks (an "anchor" and a "target") within
    a defined target zone.
    """

    # Default parameters for the target zone and fanout, inspired by common practice.
    # These can be tuned for different requirements.
    DEFAULT_FANOUT_SIZE = 5
    DEFAULT_TARGET_T_MIN = 3       # Min time delta between anchor and target (in frames)
    DEFAULT_TARGET_T_MAX = 100     # Max time delta
    DEFAULT_TARGET_F_RANGE = 20    # Freq range around anchor's freq (in mel bins)

    def __init__(self, fanout_size: int = DEFAULT_FANOUT_SIZE,
                 target_t_min: int = DEFAULT_TARGET_T_MIN,
                 target_t_max: int = DEFAULT_TARGET_T_MAX,
                 target_f_range: int = DEFAULT_TARGET_F_RANGE):
        """
        Initializes the Fingerprinter with specific parameters.

        Args:
            fanout_size (int): The maximum number of target peaks to pair with each anchor peak.
            target_t_min (int): The minimum time offset (in frames) for the target zone.
            target_t_max (int): The maximum time offset (in frames) for the target zone.
            target_f_range (int): The range of frequency bins (+/-) around an anchor's frequency
                                  to search for target peaks.
        """
        self.fanout_size = fanout_size
        self.target_t_min = target_t_min
        self.target_t_max = target_t_max
        self.target_f_range = target_f_range

        logger.debug(f"Initialized Fingerprinter with fanout={fanout_size}, "
                    f"t_min={target_t_min}, t_max={target_t_max}, f_range={target_f_range}")

    def generate_fingerprints(self, peaks: np.ndarray) -> List[Tuple[str, int]]:
        """
        Takes an array of peaks and generates a list of fingerprints.

        Each fingerprint is a tuple containing a unique hash and the absolute
        time offset of the anchor peak that generated it.

        Args:
            peaks (np.ndarray): A 2D array of peaks, where each row is
                                [time_idx, freq_idx, amplitude].
                                It's assumed to be the output of the PeakPicker.

        Returns:
            List[Tuple[str, int]]: A list of fingerprints. Each fingerprint is a
                                   tuple of (hash_hex_string, anchor_time_frame).
        """
        if peaks.shape[0] < 2:
            logger.warning("Not enough peaks to generate fingerprints.")
            return []

        # Sort peaks by time index for efficient processing. This is a crucial optimization.
        peaks = peaks[peaks[:, 0].argsort()]
        logger.info(f"Generating fingerprints from {len(peaks)} peaks")

        fingerprints = []
        
        # Iterate through each peak, treating it as an anchor
        for i in range(len(peaks)):
            anchor_time, anchor_freq, _ = peaks[i]
            logger.debug(f"Anchor peak @time={anchor_time}, freq={anchor_freq}")
            
            targets_found = 0
            
            # Iterate through subsequent peaks to find targets in the zone
            for j in range(i + 1, len(peaks)):
                target_time, target_freq, _ = peaks[j]
                
                dt = target_time - anchor_time
                
                # Check if we are outside the max time delta; if so, we can break
                # early since the peaks are time-sorted.
                if dt > self.target_t_max:
                    break
                
                # Check if the target is within the valid time and frequency zone
                if self.target_t_min <= dt <= self.target_t_max:
                    df = abs(target_freq - anchor_freq)
                    if df <= self.target_f_range:
                        # If a valid target is found, create the hash
                        h = self._create_hash(anchor_freq, target_freq, dt)
                        
                        # Store the hash along with the anchor's absolute time
                        fingerprints.append((h, int(anchor_time)))
                        logger.debug(f" ↳ Target peak @time={target_time}, freq={target_freq}, "
                                     f"dt={dt}, df={df}, hash={h}")
                        
                        targets_found += 1
                        # Enforce the fanout limit
                        if targets_found >= self.fanout_size:
                            break

        logger.info(f"Generated {len(fingerprints)} fingerprints total")                 
        return fingerprints
    
    def _create_hash(self, freq1: int, freq2: int, dt: int) -> str:
        """
        Creates a SHA-1 hash from the frequencies of two peaks and their time delta.
        """
        hash_input = f"{int(freq1)}|{int(freq2)}|{int(dt)}".encode('utf-8')
        return hashlib.sha1(hash_input).hexdigest()[:20] 