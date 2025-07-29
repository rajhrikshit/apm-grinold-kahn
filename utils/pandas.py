import pandas as pd
import numpy as np

def pw_index(stocks):
    pwi = stocks.groupby('date')['price'].mean()
    return pwi

def to_portfolio_ts(bskt_ts, wt=None):
    if wt is None:
        bskt_ts['wt'] = 1/bskt_ts.groupby('date')['ret'].transform(lambda x: x.index.get_level_values(level='ticker').nunique())

    bskt_ts['wt_ret'] = bskt_ts['ret']*bskt_ts['wt']
    port = bskt_ts.groupby('date')['wt_ret'].sum().rename('ret')
    return port

def beta(y, X):
    # OLS beta
    if isinstance(y, pd.Series):
        y = y.values
    if isinstance(X, pd.Series) or isinstance(X, pd.DataFrame):
        X = X.values
    if X.ndim == 1:
        X = X.reshape(-1, 1)
    return np.linalg.inv(X.T@X)@X.T@y