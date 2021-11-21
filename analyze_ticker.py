import pandas as pd
import numpy as np
import yfinance as yf
import datetime as dt
from pandas_datareader import data as pdr
from ta.trend import SMAIndicator
from ta.volatility import BollingerBands

from bs4 import BeautifulSoup
import requests


yf.pdr_override ()

def get_avwap (df):
    df['avg price vol'] = ((df['High'] + df['Low'] + df['Adj Close'])/3) * df['Volume']
    df['avg price vol cum sum'] = df['avg price vol'].cumsum()
    df['vol cum sum'] = df['Volume'].cumsum()
    df['AWVAP'] = df['avg price vol cum sum'] / df['vol cum sum']
    return round(df.tail(1).iloc[0]['AWVAP'],2)

def get_ticker_df (stock, start = dt.datetime.now() - dt.timedelta(days=300), end = dt.datetime.now()):
    #stock = input ("Enter a stock ticker symbol: ")
    #stock = "TSLA"

    #start = dt.datetime (2019, 1, 1)
    #end = dt.datetime (2020, 1, 1)

    RECENT_HIGH_DAYS = 6

    df = pdr.get_data_yahoo (stock, start, end)

    # Fill in SMA

    col_name = "Adj Close"

    indicator_sma = SMAIndicator(close=df[col_name], window=5, fillna=True)

    df["SMA_5"] = indicator_sma.sma_indicator()


    indicator_sma = SMAIndicator(close=df[col_name], window=20, fillna=True)

    df["SMA_20"] = indicator_sma.sma_indicator()


    indicator_sma = SMAIndicator(close=df[col_name], window=50, fillna=True)

    df["SMA_50"] = indicator_sma.sma_indicator()

    indicator_sma = SMAIndicator(close=df[col_name], window=150, fillna=True)

    df["SMA_150"] = indicator_sma.sma_indicator()

    indicator_sma = SMAIndicator(close=df[col_name], window=200, fillna=True)

    df["SMA_200"] = indicator_sma.sma_indicator()

    #indicator_sma = SMAIndicator(close=df["Volume"], window=20, fillna=True)

    #df["Volume_SMA_20"] = indicator_sma.sma_indicator()

    df["Volume_SMA_20"] = df.rolling(window=20)['Volume'].mean()

    df["RVolume"] = df["Volume"] / df["Volume_SMA_20"]

    df["Closing Range"] = (df["Adj Close"] - df["Low"]) / (df["High"] - df["Low"]) 

    indicator_bb = BollingerBands(close=df["Adj Close"], window=15, window_dev=2)

    # Add Bollinger Bands features
    df['BB High'] = indicator_bb.bollinger_hband()
    df['BB Low'] = indicator_bb.bollinger_lband()

    high_vol = df["RVolume"] > 1.2
    high_dcr = df["Closing Range"] > .6
    low_dcr = df["Closing Range"] < .3
    df.loc[high_vol & high_dcr, "AccDist"] = "A" 
    df.loc[high_vol & low_dcr, "AccDist"] = "D" 

    return df

def get_ticker_details (stock):
    #stock = input ("Enter a stock ticker symbol: ")
    #stock = "TSLA"

    #start = dt.datetime (2019, 1, 1)
    #end = dt.datetime (2020, 1, 1)

    RECENT_HIGH_DAYS = 6

    #start = dt.datetime.now() - dt.timedelta(days=300)
    #end = dt.datetime.now()

    df = get_ticker_df(stock)

    ticker_info_df = df.tail(1)

    ticker_info_dict = {"Symbol":stock}
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

    # Cross KMA

    if ticker_info_df.iloc[0]["SMA_20"] >= ticker_info_df.iloc[0]["Low"] and ticker_info_df.iloc[0]["SMA_20"] < ticker_info_df.iloc[0]["High"]:
        if ticker_info_df.iloc[0]["Adj Close"] >= ticker_info_df.iloc[0]["SMA_20"]:
            ticker_info_dict ["X20"] = 1
        else:
            ticker_info_dict ["X20"] = -1    
    else:
        ticker_info_dict ["X20"] = 0

    if ticker_info_df.iloc[0]["SMA_50"] >= ticker_info_df.iloc[0]["Low"] and ticker_info_df.iloc[0]["SMA_50"] < ticker_info_df.iloc[0]["High"]:
        if ticker_info_df.iloc[0]["Adj Close"] >= ticker_info_df.iloc[0]["SMA_50"]:
            ticker_info_dict ["X50"] = 1
        else:
            ticker_info_dict ["X50"] = -1    
    else:
        ticker_info_dict ["X50"] = 0

    # Rel Vol (Daily)

    ticker_info_dict ["RVolume"] = ticker_info_df.iloc[0]["RVolume"].round(2)
      
    # KMA Pinch

    kma_max = max([ticker_info_df.iloc[0]["SMA_50"], ticker_info_df.iloc[0]["SMA_20"], ticker_info_df.iloc[0]["SMA_200"]])
    kma_min = min([ticker_info_df.iloc[0]["SMA_50"], ticker_info_df.iloc[0]["SMA_20"], ticker_info_df.iloc[0]["SMA_200"]])

    ticker_info_dict ["KMA Pinch"] = round(abs(kma_max - kma_min)/kma_max, 2)

    # Get High and Low AWAP

    high_rec = df[df['High']==df['High'].max()] 
    high_date = high_rec.index[0]    

    ticker_info_dict ["High Date"] = high_date.strftime('%Y-%m-%d')

    df_from_high = df.loc[high_date:]
    ticker_info_dict ["AVWAP High"] = get_avwap (df_from_high)

    # Check if high is recent -- get low depending on result

    delta = pd.Timestamp.today() - high_date

    if delta.days < RECENT_HIGH_DAYS:
        low_rec = df[df['Low']==df['Low'].min()] 
    else:
        low_rec = df_from_high[df_from_high['Low']==df_from_high['Low'].min()] 
        
    low_date = low_rec.index[0]    

    ticker_info_dict ["Low Date"] = low_date.strftime('%Y-%m-%d')

    df_from_low = df.loc[low_date:]
    ticker_info_dict ["AVWAP Low"] = get_avwap (df_from_low)

    if ticker_info_dict["price"] > ticker_info_dict["AVWAP High"]:
        ticker_info_dict ["GT_AVWAP"] = 1
    elif ticker_info_dict["price"] <= ticker_info_dict["AVWAP Low"]:
        ticker_info_dict ["GT_AVWAP"] = -1
    else:
        ticker_info_dict ["GT_AVWAP"] = 0        

    ticker_info_dict ["Closing Range"] = ticker_info_df.iloc[0]["Closing Range"].round(2)

    # AVWAP Pinch

    ticker_info_dict ["AVWAP Pinch"] = round((ticker_info_dict ["AVWAP High"] - ticker_info_dict ["AVWAP Low"])/ticker_info_dict ["AVWAP High"], 2)

    # Acc Dist Day

    if ticker_info_df.iloc[0]["AccDist"] == "A":
        ticker_info_dict ["AD Day"] = 1
    elif ticker_info_df.iloc[0]["AccDist"] == "D":            
        ticker_info_dict ["AD Day"] = -1
    else:
        ticker_info_dict ["AD Day"] = 0        


    # buy sell signal

    ticker_info_dict ["Signal"] = "-"

    if ticker_info_dict ["AD Day"] == 1:
        if ticker_info_dict ["X20"] == 1 or ticker_info_dict ["X50"] == 1:
            if ticker_info_dict ["GT50"] == 1:
                ticker_info_dict ["Signal"] = "Buy"
    elif ticker_info_dict ["AD Day"] == -1:
        if ticker_info_dict ["X20"] == -1 or ticker_info_dict ["X50"] == -1:
            ticker_info_dict ["Signal"] = "Sell"

    # BB Indicator

    ticker_info_dict["BB Status"] = '-'

    if ticker_info_dict["price"] > ticker_info_df.iloc[0]["BB High"] :
        ticker_info_dict["BB Status"] = 'Extended'

    if ticker_info_dict["price"] < ticker_info_df.iloc[0]["BB Low"] :
        ticker_info_dict["BB Status"] = 'Oversold'

    # MM Trend Template Indicator

    highval = df["Adj Close"].max()
    lowval = df["Adj Close"].min()
    currval = ticker_info_df.iloc[0]["Adj Close"]
    highpct = (highval - currval) / highval
    lowpct = (currval - lowval) / lowval

    if currval > ticker_info_df.iloc[0]["SMA_50"] >= ticker_info_df.iloc[0]["SMA_150"] >= ticker_info_df.iloc[0]["SMA_200"] and highpct < .25 and lowpct > .30 :
        ticker_info_dict ["MM Trend"] = 1
    else:    
        ticker_info_dict ["MM Trend"] = 0

    # score

    ticker_info_dict ["Score"] = (ticker_info_dict ["GT200"] * 3) + (ticker_info_dict ["GT50"] * 2) + ticker_info_dict ["GT20"] + ticker_info_dict ["GT_AVWAP"] + ticker_info_dict ["AD Day"]
    #ticker_info_dict ["Score"] = ticker_info_dict ["Score"] + ticker_info_dict["BB Extreme"]

    return ticker_info_dict

def get_wishingwealth_ind ():
    url = "https://wishingwealthblog.com/"

    result = requests.get(url)
    doc = BeautifulSoup(result.text, "html.parser")

    gmi = doc.find_all(["span"], class_="indicator-value")

    ww_indicator_dict = {}

    ww_indicator_dict ["GMI"] = gmi[0].string
    ww_indicator_dict ["T2108"] = gmi[2].string
    return (ww_indicator_dict)

def get_kpi():
    kpi_dict = {}
    kpi_tickers = ['QQQ', 'SPY', 'FFTY']

    for ticker in kpi_tickers:
        ticker_info = get_ticker_details(ticker)
        if ticker_info ["GT200"] == 1 and ticker_info ["GT50"] == 1 and ticker_info ["GT20"] == 1:
            indicator = 1
        elif ticker_info ["GT200"] == 1 and ticker_info ["GT50"] == 1 and ticker_info ["GT20"] == 0:
            indicator = 0
        else:
            indicator = -1

        kpi_dict [ticker] = indicator

    return kpi_dict

def get_ticker_details_multiple (stocklist):
    # accept stocklist a list of stocks
    
    stockdetailsdict = {}

    for stock in stocklist:
        stock = stock.upper().strip()
        stockdatadict = get_ticker_details (stock)
        stockdetailsdict[stockdatadict["Symbol"]] = stockdatadict

    df = pd.DataFrame.from_dict(stockdetailsdict, orient ='index')
    df = df.sort_values("Score")
    stockdetailsdict = df.to_dict(orient ='index')


    return stockdetailsdict

def main():
    #stock = input ("Enter Symbol: ")
    #stock_data = get_ticker_details (stock)
    #print (stock_data)

    #kpi = get_kpi()
    #print (kpi)

    details = get_ticker_details_multiple(['AAPL', 'TSLA', 'AMD'])

    print (details )
    

if __name__=="__main__":
    main ()