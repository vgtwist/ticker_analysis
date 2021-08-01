import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
from ta.trend import SMAIndicator

yf.pdr_override ()

def get_avwap (df):
    df['avg price vol'] = ((df['High'] + df['Low'] + df['Adj Close'])/3) * df['Volume']
    df['avg price vol cum sum'] = df['avg price vol'].cumsum()
    df['vol cum sum'] = df['Volume'].cumsum()
    df['AWVAP'] = df['avg price vol cum sum'] / df['vol cum sum']
    return round(df.tail(1).iloc[0]['AWVAP'],2)

def get_ticker_details (stock):
    #stock = input ("Enter a stock ticker symbol: ")
    #stock = "TSLA"

    #start = dt.datetime (2019, 1, 1)
    #end = dt.datetime (2020, 1, 1)

    start = dt.datetime.now() - dt.timedelta(days=300)
    end = dt.datetime.now()

    print(end)
    df = pdr.get_data_yahoo (stock, start, end)

    # Fill in SMA

    col_name = "Adj Close"

    indicator_sma = SMAIndicator(close=df[col_name], window=5, fillna=True)

    df["SMA_5"] = indicator_sma.sma_indicator()


    indicator_sma = SMAIndicator(close=df[col_name], window=20, fillna=True)

    df["SMA_20"] = indicator_sma.sma_indicator()


    indicator_sma = SMAIndicator(close=df[col_name], window=50, fillna=True)

    df["SMA_50"] = indicator_sma.sma_indicator()

    indicator_sma = SMAIndicator(close=df[col_name], window=200, fillna=True)

    df["SMA_200"] = indicator_sma.sma_indicator()

    indicator_sma = SMAIndicator(close=df["Volume"], window=20, fillna=True)

    df["Volume_SMA_20"] = indicator_sma.sma_indicator()


    ticker_info_df = df.tail(1)

    ticker_info_dict = {}
    ticker_info_dict ["price"] = round(ticker_info_df.iloc[0]["Adj Close"], 2)

    ticker_info_dict ["Volume"] = round(ticker_info_df.iloc[0]["Volume"], 2)

    ticker_info_dict ["Avg Volume"] = round(ticker_info_df.iloc[0]["Volume_SMA_20"], 2)

    if ticker_info_df.iloc[0]["Adj Close"] > ticker_info_df.iloc[0]["SMA_50"]:
        ticker_info_dict ["GT50"] = 1
    else:
        ticker_info_dict ["GT50"] = 0

    if ticker_info_df.iloc[0]["Adj Close"] > ticker_info_df.iloc[0]["SMA_200"]:
        ticker_info_dict ["GT200"] = 1
    else:
        ticker_info_dict ["GT200"] = 0

    if ticker_info_df.iloc[0]["Adj Close"] > ticker_info_df.iloc[0]["SMA_20"]:
        ticker_info_dict ["GT20"] = 1
    else:
        ticker_info_dict ["GT20"] = 0

    if ticker_info_df.iloc[0]["Adj Close"] > ticker_info_df.iloc[0]["SMA_5"]:
        ticker_info_dict ["GT5"] = 1
    else:
        ticker_info_dict ["GT5"] = 0

    # Get High and Low AWAP

    high_rec = df[df['High']==df['High'].max()] 
    high_date = high_rec.index[0]    

    ticker_info_dict ["High Date"] = high_date

    df_from_high = df.loc[high_date:]
    ticker_info_dict ["AVWAP High"] = get_avwap (df_from_high)

    low_rec = df_from_high[df_from_high['Low']==df_from_high['Low'].min()] 
    low_date = low_rec.index[0]    

    ticker_info_dict ["Low Date"] = low_date

    df_from_low = df.loc[low_date:]
    ticker_info_dict ["AVWAP Low"] = get_avwap (df_from_low)


    return ticker_info_dict