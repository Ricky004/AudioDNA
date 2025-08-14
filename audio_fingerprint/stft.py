import numpy as np
from numpy.lib import stride_tricks

class STFT:
    def __init__(self, fft_size=1024, hop_size=512, window_type="hann") -> None:
        self.fft_size = fft_size
        self.hop_size = hop_size
        self.window_type = window_type
        
    def stft(self, x):
        if self.window_type == "hann":
            window = np.hanning(self.fft_size)
        elif self.window_type == "hamming":
            window = np.hamming(self.fft_size)
        else:
            window = np.ones(self.fft_size)

        frame = stride_tricks.sliding_window_view(x, self.fft_size)[::self.hop_size]

        frame_windowed = frame * window

        spectrum = np.fft.rfft(frame_windowed, n=self.fft_size, axis=1)

        return spectrum 