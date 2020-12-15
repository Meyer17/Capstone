import numpy as np

def note(x): #brute force way of converting numbers to notes, there's probably a predefined function for this that I 
    #couldn't find that probably cuts the run time into 1/10 but oh well
    i = x % 12
    j = np.floor(x/12) -1
    if(i==0):
        letter = chr(67)
    elif(i==1):
        letter = chr(67) +"#"
    elif(i==2):
        letter = chr(68)
    elif(i==3):
        letter = chr(68) +"#"
    elif(i==4):
        letter = chr(69)
    elif(i==5):
        letter = chr(70)
    elif(i==6):
        letter = chr(70) + "#"
    elif(i==7):
        letter = chr(71)
    elif(i==8):
        letter = chr(71) +"#"
    elif(i==9):
        letter = chr(65)
    elif(i==10):
        letter = chr(65) +"#"
    elif(i==11):
        letter = chr(66)
    return letter + "{}".format(int(j))
        
def notes(input): #Takes array of midi numbers and converts them into string values
    notes = []
    for i in range(len(input)):
        notes.append(note(input[i]))
    return notes

def compress(input): #Takes the array notes and compresses it down into the notes and their absolute length
    #Creating the first value in the list
    st = input[0]
    i = 1
    while(st == input[i]):
        i += 1
    output = [[st,i]] #creating 2d list, first value = note, second value = length
    st = input[i]
    counter = 0
    #looping through the rest of the list
    for j in range(i,len(input)):
        if(st != input[j]):
            output.append([st, counter])
            counter = 0
            st = input[j]
        counter += 1
    #Adding the final value
    output.append([st, counter])
    return output

def length(input): #takes compressed array and returns a list containing all the different lengths, ordered smallest to largest
    lengths = []
    lengths.append(input[1][1])#adding first value
    #adding other values
    for i in range(len(input)):
        check = True 
        for j in range(len(lengths)):
            if(input[i][1] == lengths[j]):
                check = False
        if(check):
            lengths.append(input[i][1])
    
    #sorting values into smallest to largest
    index = 0
    while(index < len(lengths)-1): #absolutely archaic sorting algorithm lmao
        if(lengths[index] > lengths[index + 1]):
            temp = lengths[index]
            lengths[index] = lengths[index+1]
            lengths[index+1] = temp
            index = 0
        else:
            index += 1
    return lengths

def total_length(input): #returns the "length" of the song
    sum = 0
    for i in range(len(input)):
        sum += input[i][1]
    return sum

def quarter_note(leng, t):#beeeg logic time, decides what length is a quarter note
    #to prevent accidentally altering the input
    Len = leng.copy()
    #Gets rid of dotted notes within the copied length
    index = 0
    while(index < len(Len)):
        if(t % Len[index] != 0): #dotted notes won't evenly divide the total length (hypothetically) and thus are yeeted from existence
            Len.pop(index)#will need to make this code give some leeway at some point
        else:
            index += 1
    measure = Len[-1] #there's many ways to do sheet music, this is just assuming that the measures are as long as the longest note (which is typically a whole note and therefore true)
    #Checking for common time signatures
    for i in range(len(Len)):#Checking for  4 4 time
        if(measure/4 == Len[i]):
            return Len[i]
    for i in range(len(Len)):#Checking for 3 4 time
        if(measure/3 == Len[i]):
            return Len[i]
    for i in range(len(Len)):#Checking for 2 4 time
        if(measure/2 == Len[i]):
            return Len[i] 
    return Len[0] #returns the smallest full note as a last ditch attempt

#rework of relative length function
#Takes list of compressed notes with absolute lengths and converts to relative lengths
def relative_length(input, quarter):
    out = input.copy()
    for i in range(len(out)):
        out[i][1] = out[i][1] / quarter
    return out

#will take an array of notes and will return an array of all the notes with accidentals, ordered,
#Input array must only contain notes with sharps and the output will not have the accidental
#Ex: [F#2, C#3, G1, C#4] --> [C, F]),
def accidentals(input):
    #Couldn't figure out a way to get .copy() to work rip
    output = []
    for i in range(len(input)):
        output.append(input[i][0])
    
    index = 0
    #Removing notes without accidentals
    while(index < len(output)):
        if(len(output[index]) == 2): #if there is no accidental the string length will be 2
            output.pop(index)
        else:
            index += 1
     
    #Removing the octave information from the notes / the sharp symbol
    for i in range(len(output)):
        output[i] = output[i][:1]
        
    #Removing repeat tones
    for i in range(len(output)): 
        index = i+1 #+1 avoids removing oneself
        while(index < len(output)):
            if(output[i] == output[index]):
                output.pop(index)
            else:
                index += 1

    return output

#Determins the key signature given a list of notes, list can be in either relative or absolute lengths
#Key signature is outputted as a number, + = how many sharps, - = how many flats
#Still a WIP, cannot handle notes outside of the keysignature, always makes 5/7 accidentals sharp
def key_sig(input):
    #Getting the tones
    acc = accidentals(input)
    #if there are no accidentals then the key signature is blank
    if(len(acc) == 0):
        return 0
    
    #Creating templates to compare to
    sharps = [ord("F"), ord("C"),ord("G"),ord("D"),ord("A"),ord("E"),ord("B")]
    flats = [ord("A"), ord("D"), ord("G"), ord("C"), ord("F"), ord("B"), ord("E")]
    
    #Cutting templates to the right size
    for i in range(7-len(acc)):
        sharps.pop()
        flats.pop()
    
    #finding the sum of the ascii values of the array acc and comparing to templates
    sum = 0 #getting sum
    for i in range(len(acc)):
        sum += ord(acc[i])
    #comparing values
    if(sum == np.sum(sharps)):
        return len(acc)
    if(sum == np.sum(flats)):
        return -1 * len(acc) # - integer indicates that the accidentals are flats
    
    return 0 #returns 0 if all else fails

#Takes an array of notes and a key signature and alters the notes to match the key signature
def convert_to_keysig(input, keysig):
    if(keysig >= 0):
        return #change is only needed if the key signature contains flats
    flats = ["A#", "D#", "G#", "C#", "F#", "B#", "E#"]
    conversion = ["B-", "E-", "A-", "D-", "G-", "C-", "F-"]
    #getting lists to proper lengths
    for i in range(7-np.abs(keysig)):
        flats.pop()
        conversion.pop()
    #goes through input, if it contains a value that matches a note which should be a flat, it is converted
    for i in range(len(input)):
        if(len(input[i][0]) == 3):
            for j in range(np.abs(keysig)):
                if(input[i][0][:2] == flats[j]):
                    input[i][0] = conversion[j]
                    break
    return

def sheet_input(input):#Takes the raw data and outputs a list to be converted into sheet music
    #converting raw data into compressed note format with absolute lengths
    Notes = notes(input)
    c_notes = compress(Notes)
    
    #Calculating the key signature and altering the notation of notes
    key_signature = key_sig(c_notes)
    convert_to_keysig(c_notes, key_signature)
    
    #determining the relative note lengths
    lengths = length(c_notes)
    time = total_length(c_notes)
    time = time + (time%4) #ensures for now that time is divisible by 4
    quarter, time_signature = quarter_note(lengths, time)
    
    #converting compressed notes into notes containg relative lengths
    c_notes = relative_length(c_notes, quarter)
    
    return c_notes, time_signature, key_signature#, time, lengths, quarter, table