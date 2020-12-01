import numpy as np
import matplotlib.pyplot as plt
from scipy.signal import argrelextrema
from scipy.ndimage import gaussian_filter1d


class PeakDetector:
    """ PeakDetector class finds the local maximum of the spectrogram frame by
        first convolving it with a gaussian function and then filtering it
        through selected thresholds. There are three parameters in total for
        this method of peak detection; them being the gaussian, the base line
        noise threshold, and the selection threshold.

        Attributes
        ----------
        peak_thrs : float
            threshold on which peaks must be greater than in value
        noise_thrs : float
            threshold on which data less than should be ignored
        gauss_sigma : float
            the standard deviation of the gaussian function that will
            be convolved with the spectrogram of the audio frame. 
            (default is 1.0)
        
        Methods
        -------
        get_peaks(frame)
            Returns a set of peak frequency and amplitude points of the
            spectrogram of the audio frame.
    """

    def __init__(self, max_thrs, noise_thrs, gauss_sigma=1.0, padding_fctr=4):
        """ 
            Parameters
            ----------
            max_thrs : float
                threshold on which peaks must be greater than in value
            noise_thrs : float
                threshold on which data less than should be ignored
            gauss_sigma : float, optional
                the standard deviation of the gaussian function that will
                be convolved with the spectrogram of the audio frame.
                (default is 1.0)
            padding_fctr : float, optional
                The padding factor is a factor applied to the length of
                an audio frame to determine the zero padded length of the
                spectrogram of that audio frame. (default is 4)
        """
        self.peak_thrs = max_thrs
        self.noise_thrs = noise_thrs
        self.gauss_sigma = gauss_sigma
        self.padding_fctr = padding_fctr

    def get_peaks(self, frame):
        """ Returns a set of peaks with their frequency and amplitude values
            from the smoothed gaussian convolved spectrogram frame.            
        """
        padded_spectrogram = self.__convolve_spectrogram(np.absolute(self.__sfft(frame.data)))
        spectrogram = padded_spectrogram[:int(len(padded_spectrogram)/2)]
        peaks = argrelextrema(spectrogram, np.greater)

        #TODO: filter peaks through thresholds

    def __sfft(self, audio_data):
        return np.fft.fft(audio_data, len(audio_data)*self.padding_fctr)

    # smooths spectrogram
    def __convolve_spectrogram(self, power_frame):
        return gaussian_filter1d(power_frame, self.gauss_sigma)

