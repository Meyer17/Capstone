import yin
import tracking
import peak_detection as pd
import preprocessing
from preprocessing import midi, dB, Frame

import model as pm

import numpy as np
import music21 as music
import matplotlib.pyplot as plt
from scipy.io import wavfile

import sys, getopt

def run():
    np.seterr(all='raise')

    argv = sys.argv[1:]
    inputfile, outputfile, polyphony = parse_input(sys.argv[1:])

    # code below is simply here for development purposes
    # A seperate module encapsulating the functionality of
    # these modules should return all sets of sound
    # source streams to the next high-level stage of the
    # transcription pipeline


    # polyphonic input
    if polyphony > 1:
        #TODO: check if model parameters are stored locally and are valid
        #before deciding to train model
        #model = pm.Model
        #model = pm.train_model(model)
        model = pm.load_model()
        #TODO: store runner module constants elsewhere and add configurability
        #options to command line
        frames = preprocessing.process(inputfile, 4096, 2048)
        frame_pitches = []
        for frame in frames:
            pitches = pm.estimate_pitches(frame, model, polyphony)
            frame_pitches.append(pitches)
            print(pitches)
        #TODO: track polyphonic pitches and print to same sheet music file
        return

    # monophonic input
    try:
        smpl_rate, data = wavfile.read(inputfile)
    except FileNotFoundError:
        print('Input File Not Found')
        print('shtmkr -i <inputfile> -o <outputfile> -p <polyphony>')
        return
    data = np.mean(data, axis=1) # averages audio if it is stereo

    frame_sz = int(.06 * smpl_rate) # number of samples in 60 miliseconds
    frames = np.array([data[0:frame_sz]])

    for i in range(frame_sz,len(data)-frame_sz,frame_sz):
        frames = np.append(frames, [data[i:i+frame_sz]], axis=0)

    # to get the time index of the pitches multiply
    # the index of the pitch by the frame size (samples)
    # and divide by the sample rate
    temp = [] #this is from max, just sneaking this in so that I have an input for my function, i'm sure there's a proper list i'm just missing
    for frame in frames:
        p = yin.get_pitch(frame, smpl_rate)
        temp.append(np.around(midi(p)))

    plt.plot(temp)
    plt.xlabel('Time')
    plt.ylabel('MIDI')
    plt.show()

    #This is max, i'm just going to tack my code onto the end of this for now, I can clean it up later :)
    sheet_notes, time_sig, key_sig = tracking.sheet_input(temp)
    print(sheet_notes)
    
    # to convert to sheet music using music21
    program_stream = music.stream.Stream()  # create stream to be filled with note values, key sig, time sig, etc

    ts_converted = str(time_sig[0]) + '/' + str(time_sig[1])  # create input for TimeSignature output: string
    program_stream_ts = music.meter.TimeSignature(ts_converted)  # adds time signature value
    program_stream.append(program_stream_ts)  # adds time signature to the stream

    program_stream_ks = music.key.KeySignature(key_sig)
    program_stream.append(program_stream_ks)

    #for i in sheet_notes:
    #    this_note = music.note.Note(i[0])  # add note name
    #    this_note.duration = music.note.duration.Duration(i[1])  # add notes' rhythms
    #    program_stream.append(this_note)  # add notes to stream
    #program_stream.show()  # print the music

    program_stream = music.stream.Stream() #create stream to fill with notes
    for i in sheet_notes:
        this_note = music.note.Note(i[0]) #attach note names
        this_note.duration = music.note.duration.Duration(i[1]*4) # *4 so that it can print in 4/4 time, appends duration of note
        program_stream.append(this_note) #adds to stream
    program_stream.show('text') #prints stream

def parse_input(input_command):
    inputfile = ''
    outputfile = ''
    polyphony = 1
    try:
        opts, args = getopt.getopt(input_command,"hi:op:",["ifile=","ofile=","poly="])
    except getopt.GetoptError:
        print('shtmkr -i <inputfile> -o <outputfile> -p <polyphony>')
        sys.exit(2)
    for opt, arg in opts:
        if opt == '-h':
            print('shtmkr -i <inputfile> -o <outputfile> -p <polyphony>')
            sys.exit()
        elif opt in ("-i", "--ifile"):
            inputfile = arg
        elif opt in ("-o", "--ofile"):
            outputfile = arg
        elif opt in ("-p", "--polyphony"):
            polyphony = int(arg)
    return inputfile, outputfile, polyphony
 