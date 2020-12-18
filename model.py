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

def estimate_pitches(frame, model, polyphony=1):
    peaks = pd.get_peaks(frame)
    peak_region = pd.get_peak_region(frame, peaks)

    fund_freqs = []
    for __ in range(polyphony):
        max_freq = 0
        max_lk = 0
        for freq in peak_region:
            freqs = np.append(np.asarray(fund_freqs), freq)
            l = likelihood(model, freqs, peaks)
            if l > max_lk:
                max_lk = l
                max_freq = freq
        fund_freqs.append(max_freq)

    return fund_freqs
 
def likelihood(model, fund_freqs, peaks):
    # peak likelihood
    likelihood = 1.0
    for f in peaks:
        freq = f[0]
        amp = f[1]
        dev, F0 = pd.min_peak_dev(freq, fund_freqs)
        harm = pd.peak_harmonic(freq, F0)
        ff_mean = model.freq_fund_mean
        ff_cov = model.freq_fund_cov
        if dev < .25:
            dev_p = norm(model.peak_deviation_mean, model.peak_deviation_std).pdf(dev) #p(d)
        else:
            dev_p = 0.0
        amp_p = model.kde.pdf((amp, freq, harm))/multi_norm(ff_mean, ff_cov).pdf((freq, harm)) #p(a, f, h )/p(f, h)
        s_peak_p = model.spurious_kde.pdf((freq, amp)) #p(f, a | s = 1)
        s_p = model.spurious_probability #p(s)
        likelihood *= ((1-s_p)*dev_p*amp_p) + (s_p*s_peak_p)
    return likelihood

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
    return model

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