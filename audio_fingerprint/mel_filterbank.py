import numpy as np


class MelFilterBank:
    def __init__(self, sr, n_fft, n_mels=128, fmin=0, fmax=None):
        self.sr = sr
        self.n_fft = n_fft
        self.n_mels = n_mels
        self.fmin = fmin
        self.fmax = fmax

    def hz_to_mel(self, hz):
        """Convert frequency in Hz to Mel scale."""
        return 2595 * np.log10(1 + hz / 700.0)
    
    def mel_to_hz(self, mel):
        """Convert Mel scale back to Hz."""
        return 700 * (10**(mel / 2595.0) - 1)

    def mel_filter_bank(self):
        """
        Create a Mel filter bank.
        """

        if self.fmax is None:
            self.fmax = self.sr / 2

        mel_min = self.hz_to_mel(self.fmin)
        mel_max = self.hz_to_mel(self.fmax)

        mel_points = np.linspace(mel_min, mel_max, self.n_mels + 2)

        hz_points = self.mel_to_hz(mel_points)

        bin_points = np.floor((self.n_fft + 1) * hz_points / self.sr).astype(int)

        filters = np.zeros((self.n_mels, self.n_fft // 2 + 1))
        for m in range(1, self.n_mels + 1):
            f_m_minus = bin_points[m - 1]
            f_m = bin_points[m]
            f_m_plus = bin_points[m + 1]

            for k in range(f_m_minus, f_m):
                filters[m - 1, k] = (k - f_m_minus) / (f_m - f_m_minus)
            for k in range(f_m, f_m_plus):
                filters[m - 1, k] = (f_m_plus - k) / (f_m_plus - f_m)

        return filters            

