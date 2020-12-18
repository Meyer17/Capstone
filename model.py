"""
Implements the multi pitch estimation algorithm as described in:

Duan, Z., Pardo, B., &amp; Zhang, C. (2010). Multiple Fundamental Frequency
Estimation by Modeling Spectral Peaks and Non-Peak Regions. IEEE Transactions
on Audio, Speech, and Language Processing, 18(8), 2121-2133. 
doi:10.1109/tasl.2010.2042119
"""
import yin
import peak_detection as pd
from preprocessing import midi

import numpy as np
import matplotlib.pyplot as plt
from scipy.stats import gaussian_kde, norm
from scipy.stats import multivariate_normal as multi_norm 

import pickle
from dataclasses import dataclass

chords_file = "data/random_chords.npy"
dataset_smpl_rate = 44100

MAX_POLYPHONY = 9

@dataclass
class Model:
    # binary peak classifer for spurious and normal peaks
    spurious_probability : float = 0.0

    # normal peak deviation distribution parameters
    peak_deviation_mean : float = 0.0 # in units of MIDI
    peak_deviation_std : float = 0.0

    # normal peak amplitude distribution
    kde : gaussian_kde = None
    freq_fund_mean : np.ndarray = None
    freq_fund_cov : np.ndarray = None

    # spurious peak likelihood distribution estimation
    spurious_kde : gaussian_kde = None

    #threshold for polyphonic estimation
    poly_thrs : float = .88

def estimate_pitches(frame, model):
    peaks = pd.get_peaks(frame)
    peak_region = midi(pd.get_peak_region(frame, peaks))

    fund_freqs = []
    for __ in range(MAX_POLYPHONY):
        max_freq = 0
        max_lk = 0
        for freq in peak_region:
            freqs = np.append(np.asarray(fund_freqs), freq)
            l = likelihood(model, freqs, peak_region)
            if l > max_lk:
                max_lk = l
                max_freq = freq
        fund_freqs.append(max_freq)

    num_sources = estimate_polyphony(model, fund_freqs, peak_region)
    return fund_freqs[:num_sources]


def likelihood(model, fund_freqs, peak_region):
    # peak likelihood
    likelihood = 1.0
    for f in peak_region:
        dev_p = norm(model.peak_dev_mean, model.peak_dev_std).pdf(f) #dk
        ff_mean = model.freq_fund_mean
        ff_cov = model.freq_fund_cov
        amp_p = model.kde.pdf(f)/multi_norm(ff_mean, ff_cov).pdf(f) #(a, f, h ) (f, h)
        s_peak_p = model.spurious_kde.pdf(fund_freqs) #(f, a)
        s_p = model.spurious_probability
        likelihood *= (1-s_p)*amp_p*dev_p + (s_p * s_peak_p)
    return s_p * dev_p * amp_p * s_peak_p

def estimate_polyphony(model, freqs, peak_region):
    if len(freqs) < 9:
        return -1
    m = delta(model, freqs, MAX_POLYPHONY, peak_region)
    t = model.poly_thrs
    for i in range(1,MAX_POLYPHONY):
        n = delta(model, freqs, i, peak_region)
        if n > (t*m):
            return i
    return MAX_POLYPHONY

def delta(model, freqs, n, peak_region):
    return np.log(likelihood(model, freqs[:n], peak_region)) - np.log(likelihood(model, freqs[0], peak_region))

def train_model(model):
    chords = np.load(chords_file, allow_pickle=True)

    # binary label for spurious = 1 or normal = 0
    labels = []
    # normal peak deviations in MIDI units
    devs = []
    # normal peaks
    normal_peaks = []

    #spurious peaks
    spurious_peaks = []

    for chord in chords:
        pitches = get_chord_pitches(chord)
        chord_frame = get_chord_frame(chord)
        peaks = pd.get_peaks(chord_frame)
        for peak in peaks:
            dev, pitch = pd.min_peak_dev(peak[0], pitches)
            if dev < .5:
                labels.append(0)
                devs.append(dev)
                harmonic = pd.peak_harmonic(peak[0], pitch)
                normal_peaks.append((peak[0], peak[1], harmonic))
            else:
                labels.append(1)
                spurious_peaks.append((peak[0], peak[1]))

    classifications = np.array(labels)
    print(classifications)
    print(np.mean(classifications))
    plt.hist(classifications)
    plt.show()

    devs = np.asarray(devs)
    dev_mean, dev_std = norm.fit(devs)
    print(dev_mean)
    print(dev_std)


    model.spurious_probability = np.mean(classifications)
    model.peak_deviation_mean = dev_mean
    model.peak_deviation_std = dev_std

    normal_peaks = np.asarray(normal_peaks)
    model.kde = gaussian_kde(normal_peaks.T)
    normal_peaks = np.delete(normal_peaks, 0, 1) # delete amplitude column
    freq_fund_mean = np.mean(normal_peaks, axis=0)
    freq_fund_cov = np.cov(normal_peaks, rowvar=0)
    model.freq_fund_mean = freq_fund_mean
    model.freq_fund_cov = freq_fund_cov
    print(freq_fund_mean)
    print(freq_fund_cov)

    spurious_peaks = np.asarray(spurious_peaks)
    model.spurious_kde = gaussian_kde(spurious_peaks.T)

    save_model(model)

def save_model(model, filename="model.pkl"):
    with open(filename, 'wb') as model_file:
        pickle.dump(model, model_file, pickle.HIGHEST_PROTOCOL)

def load_model(filename="model.pkl"):
    with open(filename, 'rb') as model_file:
        model = pickle.load(model_file)
    return model

def get_chord_frame(chord):
    cf = np.zeros(chord.shape[2])

    for note in chord[0:]:
        cf += note[0]
    return cf

def get_chord_pitches(chord):
    pitches = []
    for i in range(chord.shape[0]):
        note = chord[i, 0]
        pitches.append(midi(yin.get_pitch(note, dataset_smpl_rate)))
    return np.array(pitches)