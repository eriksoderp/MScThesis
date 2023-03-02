import sys
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn import preprocessing, svm
from sklearn.model_selection import train_test_split
from sklearn.linear_model import LinearRegression
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error

df = pd.read_csv(sys.argv[1])

X = np.array(df['VLMC distance']).reshape(-1, 1)
y = np.array(df['Evolutionary distance']).reshape(-1, 1)

X_train, X_test, y_train, y_test = train_test_split(X, y, random_state=42, test_size = 0.15)

regr = LinearRegression().fit(X_train, y_train)

y_pred = regr.predict(X_test)

print(f"Coefficient of determination: {regr.score(X_test, y_test)}")
print(f"Spearman R: {spearmanr(y_pred, y_test)}")
print(f"Mean squared error: {mean_squared_error(y_test, y_pred)}")
