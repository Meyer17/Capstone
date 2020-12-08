import numpy as np

def note(x): #brute force way of converting number to note, there's probably a predefined function for this that I 
    #couldn't find that probably cuts the run time into 1/10 but oh well
    i = x % 12
    j = np.floor(x/12)
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

def note_table(input):#Takes quarter note length and creates a conversion table from 32nd notes to 4 whole notes
    values = []
    values.append(-1)#to prevent a division by 0 error in relative length
    values.append(-1)#to keep the length of values an even integer
    
    for i in range(3): #adds notes smaller than quarter note
        values.append(int(input / 2**(3-i)))#full note
        values.append(int(values[-1]*1.5))#dotted note
                  
    #adds quarter note, normal/dotted
    values.append(input)#full note
    values.append(int(input*1.5))#dotted note
                  
    for i in range(4): #adds notes larger than quarter note
        values.append(input*2**(i+1))#full note
        values.append(int(values[-1]*1.5))#dotted note             
    return values

def relative_length(input, val):#Takes list of compressed notes with absolute lengths and converts to relative lengths
    out = input.copy()
    for i in range(len(out)):
        convert = True
        index = 2 #starts at 2 instead of 0 because of the 2 placeholder values we added in note_table
        while(convert): #changes absolute length to relative length of input[i]
            if(out[i][1] == val[index]):
                if(index%2 == 0):#full note
                    out[i][1] = (2**((index)/2)) / 64
                else: #dotted note
                    out[i][1] = ( 2**((index-1)/2) / 64 ) * 1.5 #steps back to the last full note then multiplies by 1.5
                convert = False #exits while loop, steps forward in for loop
            else:
                index += 1 #value not found on current index, stepping through val array 
                
                if(index >= len(val)):#to prevent an index out of bound
                    out[i][1] = 8.5 #8.5 will arbitrarily indicate an error for now
                    convert = False
    return out

def sheet_input(input):#Takes the raw data and outputs a list to be converted into sheet music
    #converting raw data into compressed note format with absolute lengths
    Notes = notes(input)
    c_notes = compress(Notes) 
    #determining the relative note lengths
    lengths = length(c_notes)
    time = total_length(c_notes)
    time = time + (time%4) #ensures for now that time is divisible by 4
    quarter = quarter_note(lengths, time)
    #converting compressed notes into notes containg relative lengths
    table = note_table(quarter)
    c_notes = relative_length(c_notes, table)
    return c_notes#, time, lengths, quarter, table