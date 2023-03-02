import sys
import numpy as np
import pandas as pd
import seaborn as sns
import matplotlib.pyplot as plt
from sklearn.neural_network import MLPRegressor
from sklearn.base import BaseEstimator, TransformerMixin
from sklearn.model_selection import train_test_split
from scipy.stats import spearmanr
from sklearn.metrics import mean_squared_error

class MLPR(BaseEstimator, TransformerMixin):
    def __init__(self, hidden_layer_sizes = 4000, seed = 42):
        self.hidden_layer_sizes = hidden_layer_sizes
        self.rng = np.random.RandomState(seed)
        self.seed = seed
        self.model = MLPRegressor(hidden_layer_sizes=self.hidden_layer_sizes, random_state=self.seed)
        self.model.n_layers_ = 3
        self.model.n_outputs_ = 1
        self.model.learning_rate = 'adaptive'
        self.model.learning_rate_init = 0.1
 
    def fit(self, X, y=None):
        X = np.array(X)
        
        X = X.reshape(-1,1)

        self.model.fit(X, y)
        return self

    def predict(self, X):
        X = np.array(X).reshape(-1,1)

        return self.model.predict(X)

    def score(self, X, y=None):
        X = np.array(X).reshape(-1,1)
        
        return spearmanr(self.model.predict(X), y)

if __name__ == '__main__':
    data = pd.read_csv(sys.argv[1])
    X, y = data['VLMC distance'], data['Evolutionary distance']

    X_train, X_test, y_train, y_test = train_test_split(X, y, ä test_size = 0.15)

    model = MLPR()
    model.fit(X_train, y_train)

    y_pred = model.predict(X_test)


    print(f"Coefficient of determination: {model.model.score(np.array(X_test).reshape(-1,1), y_test)}")
    print(f"Spearman R: {spearmanr(y_pred, y_test)}")
    print(f"Mean squared error: {mean_squared_error(y_test, y_pred)}")
