import numpy as np
import matplotlib.pyplot as plt
from scipy.io import wavfile
from scipy.signal import hamming
from scipy.signal import spectrogram

from dataclasses import dataclass

@dataclass
class Frame:
    """ Frame Data Class represents a frame 

        Attributes
        ----------
        data : np.array
            the segment of samples from the parent wav file
        silent : bool
            a flag used to indicate if this frame is silent
        framelen : int
            the number of samples that is held in this frame
        track_index : int
            the global time index of this frame with respect to the audio track
            it derives from
    """
    data: np.ndarray = np.array([])
    silent: bool = False
    track_index: int = 0


class AudioPreprocessor:
    """ AudioPreprocessor class generates a set of audio frames from wav file 
        so that they could be offered to the next stage of the polyphonic
        music transcription pipeline.

        Attributes
        ----------
        framelen : int
                number of data points in one frame
        frame_interval : int
                distance between frames on the time domain
        silence_thrs : float
                threshold on which silence is defined as being lower than

        Methods
        -------
        process(wav_file)
            Reads data from a wav file given its name and returns a set of
            frames of equal length. 

    """

    def __init__(self, framelen, frame_interval, silence_thrs):
        # the frame interval does not have to equal the frame length
        # since some frames may overlap eachother
        self.framelen = framelen
        self.frame_interval = frame_interval
        self.silence_thrs = silence_thrs

    def __is_silent(self, data):
        """ Detects whether a segment of audio is silent 
            
            Parameters
            ----------
            data : np.array
                audio sample data
        """
        return np.sqrt(np.mean(data**2)) < self.silence_thrs

    def process(self, wav_file):
        """ Reads in data from a wav file, zero means and rms normalizes it,
            and returns a set of discrete data frames

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

            data = np.mean(data, axis=1)
            freqs, times, Sx = spectrogram(data, fs=smpl_rate, window='hanning',
                                      nperseg=2048, noverlap=2048 - 441,
                                      detrend=False, scaling='spectrum')
            print(Sx.shape)
            Sx = np.sqrt(Sx)
            print(Sx)


        except FileNotFoundError:
            print("Error: File Not Found")
        else:
            f, ax = plt.subplots(figsize=(7, 4))
            #ax.pcolormesh(times, freqs/1000, 10 * np.log10(Sx), cmap='viridis')
            #ax.pcolormesh(Sx)

            t = np.arange(Sx.shape[1])
            t = t/smpl_rate * 1000 # milliseconds

            for i in range(Sx.shape[0]):
                plt.plot(t, Sx[i])
                plt.show()
            

            ax.set_ylabel('Frequency [kHz]')
            ax.set_xlabel('Time [ms]')
            plt.show()

            # take the average if the input is stereo channel
            if data.shape[1] == 2:
                data = (data[:, 0] + data[:, 1])/2.0

            # zero mean
            data -= np.mean(data)

            # rms normalization
            data /= np.sqrt(np.mean(data**2))

            # frame creation
            L = len(data)
            self.num_frames = int(np.floor(L/self.frame_interval) + 1)
            frames = []

            # window function
            win = hamming(self.framelen)

            for i in range(self.num_frames):
                findex = i*self.frame_interval
                frame_data = data[findex : findex + self.framelen]
                frame_data *= win[0 : len(frame_data)]
                is_silent = self.__is_silent(frame_data)
                frames.append(Frame(frame_data, is_silent, findex))
            
            print("Number of Frames: {}".format(len(frames)))

            # plot data
            if __debug__:
                plt.plot(data)
                plt.show()
            
            return frames

# returns the midi number for a pitch in htz
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
            The nearest midi number corresponding to the frequency
    """
    if pitch <= 0:
        raise ValueError
    return int(12 * np.log2(pitch/440) + 69)