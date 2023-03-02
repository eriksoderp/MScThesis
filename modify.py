import sys, getopt
import random
import os
import numpy as np
import pandas as pd
from tqdm import tqdm

def main(argv):
    input_file = ''
    output_file = ''
    number_of_sequences = 1
    number_of_letters = 0.1
    arg_help = 'modify.py -i <inputfile> -s <number_of_sequences> -l <number_of_letters> -o <outputfile>'
    try:
        opts, args = getopt.getopt(argv, "hi:s:l:o:", ["ifile=","number_of_letters=","ofile="])
    except:
        print(arg_help)
        sys.exit()
    
    for opt, arg in opts:
        if opt == '-h':
            print(arg_help)
            sys.exit()
        elif opt in ("-i", "--ifile"):
            input_file = arg
        elif opt in ("-s", "--number_of_sequences"):
            number_of_sequences = int(arg)
        elif opt in("-l", "--number_of_letters"):
            number_of_letters = float(arg)
        elif opt in ("-o", "--ofile"):
            output_file = arg
        

    print ('Input file is', input_file)
    print ('Number of sequences is', number_of_sequences)
    print ('Percent of letters to convert is', number_of_letters)
    print ('Output file is', output_file)

    first_part = output_file.split('.')[0]
    sequences, e_distances = modify(input_file, number_of_letters, number_of_sequences)
    e_distances = np.asarray(e_distances)

    distances_file_name = "modified_sequences/" + "distances_" + first_part + ".csv"
    os.makedirs(os.path.dirname(distances_file_name), exist_ok=True)
    pd.DataFrame(e_distances).to_csv(distances_file_name)
    
    file_name = "modified_sequences/" + output_file
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w") as f:
        f.write(sequences)
    f.close()


# number_of_letters specify how many letters to replace
def modify(input_file, number_of_letters, number_of_sequences): 
    with open(input_file, 'r') as f:
        description = next(f) # skips the description of the genome
        sequence = f.read() # parses sequence
        sequence = sequence.split('\n>')[0] # takes the first genome in a multifasta file
    f.close()

    sequence = sequence.strip()
    len_seq = int(number_of_letters*len(sequence))
    letters = ['A', 'C', 'G', 'T']*len_seq
    indices = [i for i, _ in enumerate(sequence)]
    sequences = ">Original \n" + sequence + "\n"
    result = [0]*(number_of_sequences+1)

    for s in tqdm(range(number_of_sequences)):
        count = 0
        ran = random.randrange(len_seq)
        new_letters = iter(random.sample(letters, ran))
        sam = random.sample(indices, ran)
        lst = list(sequence)
        for i in sam:
            c = next(new_letters)
            if lst[i] == c:
                count += 1
            else:
                lst[i] = c

        count = ran - count
        seq = ''.join(lst)
        new_sequence = ">Number of dissimilarities from original is " + str(count) + "\n" + seq + "\n"

        sequences += new_sequence
        result[s+1] = count / len(sequence)

    return sequences, result

if __name__ == "__main__":
    main(sys.argv[1:])