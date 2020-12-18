from preprocessing import midi, dB, hz

import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from scipy.ndimage import gaussian_filter1d


#pitch is fundamental frequency
def peak_harmonic(peak_pitch, pitch):
    f = peak_pitch
    F0 = pitch

    h = np.around(2 ** ((f - F0)/12))
    return h

# pitch is fundamental frequency
def peak_dev(peak_pitch, pitch):
    h = peak_harmonic(peak_pitch, pitch)

    if h == 0:
        return 0
    return np.abs(peak_pitch - pitch - 12*np.log2(h))

# returns deviation to nearest harmonic
def min_peak_dev(peak_pitch, pitches):
    min_dev = np.inf
    closest_F0 = 0
    dev = 0.0

    for pitch in pitches:
        dev = peak_dev(peak_pitch, pitch)
        if dev < min_dev:
            min_dev = dev
            closest_F0 = pitch
    return min_dev, closest_F0

def get_peak_region(frame, peaks, region_dev=.25, padding_fctr=4):
    freq_frame = dB(np.absolute(__sfft(frame.data, padding_fctr)))
    freq_frame = freq_frame[:int(len(freq_frame)/2)]

    peak_region = []
    min_freq = 0.0
    max_freq = 0.0
    for peak in peaks:
        min_freq = peak[0] - region_dev
        max_freq = peak[0] + region_dev
        peak_region.extend(np.arange(min_freq, max_freq, .5).tolist())
    return np.unique(peak_region)

def get_peaks(frame, peak_thrs=8, noise_thrs=50, gauss_sigma=8.0, padding_fctr=4):
    """ Returns a set of peaks with their frequency and amplitude values
        from the smoothed gaussian convolved spectrogram frame.

        Parameters
        ----------
        frame : Frame
            Raw audio frame for analysis
        peak_thrs : float
            Local threshold between peak and smoothed peak
        noise_thrs : float
            Lower global threshold measured from the maximum peak
        gauss_sigma : float
            Gaussian convolution filter parameter
        padding_fctr : float
            Zero padding factor for fast fourier transform of audio frame
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

    #if __debug__:
    #    plt.plot(freq_frame)
    #    plt.plot(smooth_freq_frame)
    #    plt.scatter(peak_freqs, peak_ampls)
    #    plt.ylabel('Amplitude (dB)')
    #    plt.xlabel('Frequency (Hz)')
    #    plt.show()

    return peak_points

def __sfft(audio_data, padding_fctr):
    return np.fft.fft(audio_data, len(audio_data)*padding_fctr)

# smooths spectrogram with a moving average filter
def __convolve_freq_frame(freq_frame, gauss_sigma):
    return gaussian_filter1d(freq_frame, sigma=gauss_sigma)
