import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import hamming
from scipy.signal import spectrogram

from dataclasses import dataclass

@dataclass
class Frame:
    """ Raw digital audio frame with subsidiary metadata

        Attributes
        ----------
        data : np.array
            the segment of samples from the parent wav file
        silent : bool
            a flag used to indicate if a frame instance is silent
        track_index : int
            the global time index of this frame with respect to the audio track
            it derives from
        smpl_rate : int
            the sample rate of the digital audio frame in units of Hz
    """
    data: np.ndarray = np.zeros(1)
    silent: bool = False
    track_index: int = 0
    smpl_rate : int = 0

def midi(pitch):
    """
        Returns the midi number representation for a pitch
        in Hz

        Parameters
        ----------
        pitch : float
            The pitch in units of Hz to convert
        
        Returns
        -------
        midi : int
            The nearest midi number corresponding to the frequency.
    """
    p = np.around(12 * np.log2(pitch/440) + 69)
    return np.int32(p)

def dB(amplitude):
    """
        Returns the log-scale amplitude for a linear amplitude value.

        Parameters
        ----------
        amplitude : float
            linear amplitude value
        
        Returns
        -------
        dB : float
            The log-scale measure(decibel) of the linear amplitude value. 
    """
    if len(amplitude) == 0:
        return amplitude
    if amplitude.all() <= 0:
        return np.zeros(len(amplitude))
    return 20 * np.log10(amplitude)

def process(wav_file, framelen, frame_interval, silence_thrs=.075):
    """ Reads in data from a wav file, zero means and rms normalizes it,
        and returns a set of discrete data frames with audio in units of dB

        Parameters
        ----------
        wav_file : str
            the name of the wav file to read from
    """

    # read wav file data
    try:
        smpl_rate, data = wavfile.read(wav_file)
        print("Sample Rate: {}".format(smpl_rate))
        print("Number of Samples: {}".format(len(data)))

    except FileNotFoundError:
        print("Error: File Not Found")
    else:
        # take the average if the input is stereo channel
        if data.shape[1] == 2:
            data = (data[:, 0] + data[:, 1])/2.0

        # zero mean
        data -= np.mean(data)

        # rms normalization
        data /= np.sqrt(np.mean(data**2))

        # frame creation
        L = len(data)
        num_frames = int(np.floor(L/frame_interval) + 1)
        frames = []

        # window function
        win = hamming(framelen)

        for i in range(num_frames):
            findex = i*frame_interval
            frame_data = data[findex : findex + framelen]
            frame_data *= win[0 : len(frame_data)]
            is_silent = __is_silent(frame_data, silence_thrs)
            frames.append(Frame(frame_data, is_silent, findex))
        
        print("Number of Frames: {}".format(len(frames)))

        # plot data
        if __debug__:
            plt.plot(data)
            plt.show()
        
        return frames

def __is_silent(data, silence_thrs):
    """ Detects whether a segment of audio is silent 
        
        Parameters
        ----------
        data : np.array
            audio sample data
    """
    return np.sqrt(np.mean(data**2)) < silence_thrs