from preprocessing import midi, dB

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from scipy.ndimage import gaussian_filter1d

def get_peaks(frame, peak_thrs=8, noise_thrs=50, gauss_sigma=8.0, padding_fctr=4):
    """ Returns a set of peaks with their frequency and amplitude values
        from the smoothed gaussian convolved spectrogram frame.
        
        Parameters
        ----------
        frame : Frame
            Raw audio frame for analysis
    """
    # get frequency frame and convolve with gaussian
    freq_frame = dB(np.absolute(__sfft(frame.data, padding_fctr)))
    freq_frame = freq_frame[:int(len(freq_frame)/2)]
    smooth_freq_frame = __convolve_freq_frame(freq_frame, gauss_sigma)

    # get extrema
    peak_freqs = argrelextrema(smooth_freq_frame, np.greater)[0]

    # filter peaks through thresholds
    floor = np.amax(freq_frame[peak_freqs]) - noise_thrs
    peak_freqs = peak_freqs[freq_frame[peak_freqs] > floor]
    local_diff = freq_frame[peak_freqs] - smooth_freq_frame[peak_freqs]
    peak_freqs = peak_freqs[local_diff > peak_thrs]
    peak_ampls = freq_frame[peak_freqs]
    
    # convert frequency peaks to units of midi and return in numpy array
    peak_midi = midi(peak_freqs)
    peak_points = np.column_stack((peak_midi, peak_ampls))


    if __debug__:
        print(peak_points)
        plt.plot(freq_frame)
        plt.plot(smooth_freq_frame)
        plt.scatter(peak_freqs, peak_ampls)
        plt.show()

    return peak_points

def __sfft(audio_data, padding_fctr):
    return np.fft.fft(audio_data, len(audio_data)*padding_fctr)

# smooths spectrogram with a moving average filter
def __convolve_freq_frame(freq_frame, gauss_sigma):
    return gaussian_filter1d(freq_frame, sigma=gauss_sigma)
