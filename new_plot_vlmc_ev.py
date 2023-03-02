import pandas as pd
import numpy as np
import seaborn as sns
import sys
import matplotlib.pyplot as plt

evo_path = sys.argv[1]
df_evo = pd.read_csv(evo_path)

vlmc_path = sys.argv[2]
df_vlmc = pd.read_csv(vlmc_path)

df = pd.DataFrame()

evo_series = pd.Series(dtype='float64')
evo_series = df_evo['0']

df['Evolutionary distance'] = evo_series

vlmc_series = pd.Series(dtype='float64')
vlmc_series = df_vlmc['0']

df['VLMC distance'] = vlmc_series

df.to_csv('distances_df.csv')

sns.set_theme()

sns.relplot(
    data=df,
    x='VLMC distance', y='Evolutionary distance'
)

plt.show()