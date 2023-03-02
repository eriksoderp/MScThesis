import pandas as pd
import numpy as np
import seaborn as sns
import sys
import matplotlib.pyplot as plt

evo_path = sys.argv[1]
df_evo = pd.read_csv(evo_path)

vlmc_path = sys.argv[2]


df = pd.DataFrame()

evo_series = pd.Series(dtype='float64')
evo_series = df_evo['0']

extension = '.csv'
temp_df = pd.DataFrame()
temp_df['Evolutionary distance'] = evo_series
for threshold, s_threshold in [(0.0,'00'), (0.5,'05'), (1.2,'12'), (3.9075,'39075')]:
    df_vlmc = pd.read_csv(vlmc_path + '_' + s_threshold + extension)
    vlmc_series = pd.Series(dtype='float64')
    vlmc_series = df_vlmc['0']
    temp_df['VLMC distance'] = vlmc_series
    temp_df['Threshold'] = threshold

    df = pd.concat([df, temp_df])

sns.set_theme()

sns.relplot(
    data=df,
    x='VLMC distance', y='Evolutionary distance', hue='Threshold'
)

plt.show()