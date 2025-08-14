import numpy as np

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

        num_frames = 1 + (len(x) - self.fft_size) # hop_sizes
        if num_frames < 1:
            num_frames = 1

        stft_matrix = np.empty((num_frames, self.fft_size), dtype=np.complex64)

        for m in range(num_frames):
            start = m * self.hop_size
            frame = x[start:start+self.fft_size]

            if len(frame) < self.fft_size:
                frame = np.pad(frame, (0, self.fft_size - len(frame)), mode='constant')

            frame_windowed = frame * window

            spectrum = np.fft.fft(frame_windowed, n=self.fft_size)

            stft_matrix[m, :] = spectrum

        return stft_matrix 