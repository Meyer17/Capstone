from preprocessing import AudioPreprocessor
from preprocessing import midi
from peak_detection import PeakDetector
import yin

import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

import sys, getopt

def main(argv):
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('test.py -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('test.py -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
    print('Input file is ' + inputfile)
    print('Output file is ' +  outputfile)

    # code below is simply here for development purposes
    # A seperate module encapsulating the functionality of
    # these modules should return all sets of sound
    # source streams to the next high-level stage of the
    # transcription pipeline

    smpl_rate, data = wavfile.read(inputfile)
    data = np.mean(data, axis=1) # averages audio if it is stereo

    frame_sz = int(.06 * smpl_rate) # number of samples in 60 miliseconds
    frames = np.array([data[0:frame_sz]])

    for i in range(frame_sz,len(data)-frame_sz,frame_sz):
        frames = np.append(frames, [data[i:i+frame_sz]], axis=0)

    pitches = np.array([])

    # to get the time index of the pitches multiply its
    # the index of the pitch by the frame size (samples)
    # and divide by the sample rate
    for frame in frames:
        p = yin.get_pitch(frame, smpl_rate)
        pitches = np.append(pitches, p)
        if p > 0:
            m = midi(p)
            print("GOT PITCH: {} MIDI ".format(m))

    plt.plot(pitches)
    plt.show()

if __name__ == "__main__":
    main(sys.argv[1:])