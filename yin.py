""" This module implements the YIN algorithm for fundamental frequency 
    of a single audio frame as described in:

    [1] Cheveigné, A. D., &amp; Kawahara, H. (2002). YIN, a fundamental 
    frequency estimator for speech and music. The Journal of the 
    Acoustical Society of America, 111(4), 1917-1930. doi:10.1121/1.1458024
"""
import numpy as np
from scipy.signal import argrelextrema

import matplotlib.pyplot as plt

def __diff(audio, max_t):
    N = len(audio)
    df = [0] * max_t
    for tau in range(1, max_t):
         for j in range(0, N-max_t):
             tmp = int(audio[j] - audio[j + tau])
             df[tau] += tmp * tmp
    return df

"""
Optimization attributed to:
https://stackoverflow.com/questions/46001299/optimize-computation-of-the-difference-function
"""
def __fast_diff(audio, max_t):
    x = np.array(audio, np.float64)
    w = x.size
    tau_max = min(max_t, w)
    x_cumsum = np.concatenate((np.array([0.]), (x * x).cumsum()))
    size = w + tau_max
    p2 = (size // 32).bit_length()
    nice_numbers = (16, 18, 20, 24, 25, 27, 30, 32)
    size_pad = min(x * 2 ** p2 for x in nice_numbers if x * 2 ** p2 >= size)
    fc = np.fft.rfft(x, size_pad)
    conv = np.fft.irfft(fc * fc.conjugate())[:tau_max]
    return x_cumsum[w:w - tau_max:-1] + x_cumsum[w] - x_cumsum[:tau_max] - 2 * conv

# cummulative mean normalized difference function
def __cumm_mean_diff(df):
    N = len(df)
    if np.sum(df[1:]) == 0:
        return np.insert(df[1:], 0, 1)
    cmndf = df[1:] * np.array(range(1, N)) / np.cumsum(df[1:]).astype(float) #scipy method
    return np.insert(cmndf, 0, 1)

# computes the yin algorithm on a single signal frame
def get_pitch(frame, smpl_rate, min_freq=20, max_freq=600, h_thrs=0.1):
    max_t = int(smpl_rate/min_freq)
    min_t = int(smpl_rate/max_freq)
    df = __fast_diff(frame, max_t)
    cmdf = __cumm_mean_diff(df)

    # returns the smallest period value that results in cmdf below threshold
    t = min_t
    while t < max_t:
        if cmdf[t] < h_thrs:
            return float(smpl_rate/t)
        t += 1
    return 0

