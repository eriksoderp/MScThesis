import sys, getopt
import random
import os
import numpy as np
import pandas as pd
import multiprocessing
import itertools
from tqdm import tqdm
import time

def main(argv):
    start = time.time()
    input_file = ''
    output_file = ''
    number_of_sequences = 1
    number_of_letters = 0.1
    number_of_cores = 1
    arg_help = 'modify.py -i <inputfile> -s <number_of_sequences> -l <number_of_letters> -p <number_of_cores> -o <outputfile>'
    try:
        opts, args = getopt.getopt(argv, "hi:s:l:p:o:", ["ifile=","number_of_letters=","ofile="])
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
        elif opt in("-p"):
            number_of_cores = int(arg)
        elif opt in ("-o", "--ofile"):
            output_file = arg
        

    print ('Input file is', input_file)
    print ('Number of sequences is', number_of_sequences)
    print ('Percent of letters to convert is', number_of_letters)
    print ('Number of cores used', number_of_cores)
    print ('Output file is', output_file)

    first_part = output_file.split('.')[0]
    sequences, e_distances = modify(input_file, number_of_letters, number_of_sequences, number_of_cores)
    e_distances = np.asarray(e_distances)

    distances_file_name = "modified_sequences/" + "distances_" + first_part + ".csv"
    os.makedirs(os.path.dirname(distances_file_name), exist_ok=True)
    pd.DataFrame(e_distances).to_csv(distances_file_name)
    
    file_name = "modified_sequences/" + output_file
    os.makedirs(os.path.dirname(file_name), exist_ok=True)
    with open(file_name, "w") as f:
        f.write(sequences)
    f.close()
    end = time.time()

    print("Time ran was:", end - start, "seconds")


# number_of_letters specify how many letters to replace
def modify(input_file, number_of_letters, number_of_sequences, number_of_cores): 
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

    ss = [s for s in range(number_of_sequences)]
    
    pool_obj = multiprocessing.Pool(number_of_cores)
    ans = pool_obj.starmap(mod_par, zip(itertools.repeat(sequence), itertools.repeat(len_seq), itertools.repeat(letters), itertools.repeat(indices), ss))

    for seq, ratio, s in ans:
        sequences += seq
        result[s+1] = ratio

    pool_obj.close()

    return sequences, result

def mod_par(sequence, len_seq, letters, indices, s):
    count = 0
    ran = random.randrange(len_seq)
    new_letters = iter(random.sample(letters, ran))
    sam = random.sample(indices, ran)
    lst = list(sequence)
    for i in sam:
        c = next(new_letters)
        if lst[i] != c:
            lst[i] = c
            count += 1

    seq = ''.join(lst)
    new_sequence = ">Number of dissimilarities from original is " + str(count) + "\n" + seq + "\n"
    ratio = count / len(sequence)

    return new_sequence, ratio, s


if __name__ == "__main__":
    main(sys.argv[1:])
