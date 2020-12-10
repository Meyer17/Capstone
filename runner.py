from preprocessing import AudioPreprocessor
from preprocessing import midi
from peak_detection import PeakDetector
import tracking
import yin
import music21 as music
import matplotlib.pyplot as plt
import numpy as np
from scipy.io import wavfile

import sys, getopt

def run():
    argv = sys.argv[1:]
    inputfile = ''
    outputfile = ''
    try:
        opts, args = getopt.getopt(argv,"hi:o:",["ifile=","ofile="])
    except getopt.GetoptError:
        print('shtmkr -i <inputfile> -o <outputfile>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('shtmkr -i <inputfile> -o <outputfile>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg

    # code below is simply here for development purposes
    # A seperate module encapsulating the functionality of
    # these modules should return all sets of sound
    # source streams to the next high-level stage of the
    # transcription pipeline
    try:
        smpl_rate, data = wavfile.read(inputfile)
    except FileNotFoundError:
        print('Input File Not Found')
        print('shtmkr -i <inputfile> -o <outputfile>')
        return
    data = np.mean(data, axis=1) # averages audio if it is stereo

    frame_sz = int(.06 * smpl_rate) # number of samples in 60 miliseconds
    frames = np.array([data[0:frame_sz]])

    for i in range(frame_sz,len(data)-frame_sz,frame_sz):
        frames = np.append(frames, [data[i:i+frame_sz]], axis=0)

    pitches = np.array([])

    # to get the time index of the pitches multiply its
    # the index of the pitch by the frame size (samples)
    # and divide by the sample rate

    temp = [] #this is from max, just sneaking this in so that I have an input for my function, i'm sure there's a proper list i'm just missing
    for frame in frames:
        p = yin.get_pitch(frame, smpl_rate)
        pitches = np.append(pitches, p)
        if p > 0:
            m = midi(p)
            temp.append(m)
            print("GOT PITCH: {} MIDI ".format(m))
    
    #This is max, i'm just going to tack my code onto the end of this for now, I can clean it up later :)
    sheet_notes = tracking.sheet_input(temp)
    print(sheet_notes)

    plt.plot(pitches)
    plt.show()
    
# to convert to sheet music using music21
    program_stream = stream.Stream() #create stream to fill with notes
    for i in sheet_notes:
        this_note = music.note.Note(i[0]) #attach note names
        this_note.duration = note.duration.Duration(i[1]*4) # *4 so that it can print in 4/4 time, appends duration of note
        program_stream.append(this_note) #adds to stream
    program_stream.show() #prints stream
