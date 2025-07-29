from datetime import datetime
import pandas as pd
import requests
from bs4 import BeautifulSoup
import yfinance as yf
from tqdm import tqdm
import duckdb
import os

DB_PATH = '<root>/sp500.db'

def sp500_tickers():
    response = requests.get('https://en.wikipedia.org/wiki/List_of_S%26P_500_companies')
    soup = BeautifulSoup(response.text, 'lxml')
    table = soup.find('table', attrs={'id': 'constituents'})
    tickers = []
    for row in table.find_all('tr')[1:]:
        data = row.find_all('td')
        if data:
            tickers.append(data[0].text.strip())
    return tickers

def components_history(start_date ='2020-01-01', end_date = datetime.today().date()):
    tickers = sp500_tickers()
    data = []
    for ticker in tqdm(tickers):
        history = yf.Ticker(ticker).history(start=start_date, end=end_date)
        history['ticker'] = ticker
        data.append(history)
    return pd.concat(data)

def save(history, table_name='history'):
    os.makedirs(os.path.dirname(DB_PATH), exist_ok=True)

    with duckdb.connect(DB_PATH) as con:
        con.execute(f"CREATE TABLE IF NOT EXISTS {table_name} AS SELECT * FROM history")
    print(f"Saved {history['ticker'].nunique()} tickers to {DB_PATH} in table `{table_name}`.\nTotal rows: {len(history)}")

def load(table_name='history', start_date='2020-01-01', end_date=datetime.today().date()):
    with duckdb.connect(DB_PATH) as con:
        qry = f"select * from {table_name} where Date between '{start_date}' and '{end_date}'"
        history = con.execute(qry).df()
        return history

def pw_index(stocks):
    pwi = stocks.groupby('Date')['Close'].mean()
    return pwi

if __name__ == '__main__':
    history = components_history(start_date='2015-01-01')
    save(history.reset_index())