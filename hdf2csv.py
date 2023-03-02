import pandas as pd
import sys
import numpy as np
import h5py

hf_path = sys.argv[1]

df = pd.DataFrame(np.array(h5py.File(hf_path)['distances']['dvstar-0']))

df.to_csv(sys.stdout)