""" This module implements the YIN algorithm for fundamental frequency 
    of a single audio frame as described in:

    [1] Cheveigné, A. D., &amp; Kawahara, H. (2002). YIN, a fundamental 
    frequency estimator for speech and music. The Journal of the 
    Acoustical Society of America, 111(4), 1917-1930. doi:10.1121/1.1458024
"""
import numpy as np
from scipy.signal import argrelextrema

import matplotlib.pyplot as plt

# difference function
def __diff(audio, max_t):
    N = len(audio)
    df = [0] * max_t
    for tau in range(1, max_t):
         for j in range(0, N-max_t):
             tmp = int(audio[j] - audio[j + tau])
             df[tau] += tmp * tmp
    return df

# cummulative mean normalized difference function
def __cumm_mean_diff(df):
    N = len(df)
    cmndf = df[1:] * np.array(range(1, N)) / np.cumsum(df[1:]).astype(float) #scipy method
    return np.insert(cmndf, 0, 1)

# computes the yin algorithm on a single signal frame
def get_pitch(frame, smpl_rate, min_freq=20, max_freq=600, h_thrs=0.1):
    """
        Retrieves the fundamental frequency of an audio frame by applying
        the yin algorithm.

        Parameters
        ----------
        frame : np.array
            Array of audio amplitude data
        smpl_rate : int 
            Frequency in Hz at which audio frame is sampled at
        min_freq : float, optional
            Min frequency that should be expected in audio frame.
            (default is 20Hz)
        max_freq : float, optional
            Max frequency that should be searched for in audio frame. 
            (default is 600Hz)
        h_thrs : float, optional
            Absolute harmonic threshold that defines the boundary on the
            difference function for determining pitch period.
        
        Returns
        -------
        pitch : float
            The fundamental frequency of the audio frame in Hz.
    """
    max_t = int(smpl_rate/min_freq)
    min_t = int(smpl_rate/max_freq)
    df = __diff(frame, max_t)
    cmdf = __cumm_mean_diff(df)

    # returns the smallest period value that results in cmdf below threshold
    # TODO: test with just a search space over the minimum of the cmdfs
    t = min_t
    while t < max_t:
        if cmdf[t] < h_thrs:
            return float(smpl_rate/t)
        t += 1
    return 0

