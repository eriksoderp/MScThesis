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
for index, row in df_evo.iterrows():
    evo_series = evo_series.append(row[1:index+2], ignore_index=True)

df['Evolutionary distance'] = evo_series

vlmc_series = pd.Series(dtype='float64')
for index, row in df_vlmc.iterrows():
    vlmc_series = vlmc_series.append(row[1:index+2], ignore_index=True)

df['VLMC distance'] = vlmc_series

df.to_csv('distances_df.csv')

sns.set_theme()

sns.relplot(
    data=df,
    x='Evolutionary distance', y='VLMC distance'
)

plt.savefig(sys.argv[3])
plt.show()