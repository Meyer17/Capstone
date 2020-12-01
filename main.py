from preprocessing import AudioPreprocessor
from peak_detection import PeakDetector

import matplotlib.pyplot as plt
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
    processor = AudioPreprocessor(2048, 441, 8)
    peak_detector = PeakDetector(100, 8)
    audio_frames = processor.process(inputfile)

    for frame in audio_frames:
        peak_detector.get_peaks(frame)

if __name__ == "__main__":
    main(sys.argv[1:])