import pandas as pd
import numpy as np
import seaborn as sns
import sys
import matplotlib.pyplot as plt

df = pd.read_csv("dataset.csv")

sns.set_theme()

sns.relplot(
    data=df,
    x='VLMC distance', y='Evolutionary distance', hue='Threshold'
)

plt.show()
