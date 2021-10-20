import json
from os import error
import requests
import pandas as pd
from pypfopt import EfficientFrontier
from pypfopt import risk_models
from pypfopt import expected_returns
from pypfopt.discrete_allocation import DiscreteAllocation, get_latest_prices
from datetime import datetime
import yfinance as yf

def getStockHistory2(ticker_):
    ticker = yf.Ticker(ticker_)
    hist = ticker.history(period="max")
    outname = ticker_ + '.csv'
    hist.to_csv(outname, index=True)
    # print(type(hist))
    # hist.head()
    # print(hist.columns)
    # hist.rename(columns={"Close", "AAPL"})
    # print(hist)


def getStockHistory(ticker):
    if True:
        pass
    else:
        url = 'http://tbankonline.com/SMUtBank_API/Gateway'
        # Header
        serviceName = 'getStockHistory'
        userID = '01332738'
        PIN = '877324'
        OTP = '999999'
        # Content
        symbol = ticker
        startDate = datetime.utcfromtimestamp(0).strftime('%Y-%m-%d')
        endDate = datetime.now().strftime('%Y-%m-%d')

        headerObj = {
            'Header': {
                'serviceName': serviceName,
                'userID': userID,
                'PIN': PIN,
                'OTP': OTP
            }
        }
        contentObj = {
            'Content': {
                'symbol': symbol,
                'startDate': startDate,
                'endDate': endDate
            }
        }
        final_url = "{0}?Header={1}&Content={2}".format(
            url, json.dumps(headerObj), json.dumps(contentObj))
        response = requests.post(final_url)
        print(response.content)
        serviceRespHeader = response.json(
        )['Content']['ServiceResponse']['ServiceRespHeader']
        errorCode = serviceRespHeader['GlobalErrorID']
        print(errorCode)
        if errorCode == '010000':
            stockHistory = json.loads(response.json()[
                                    'Content']['ServiceResponse']['Stock_History']['jsonTimeSeries'])['chart']['result'][0]
            print("stockHistory", stockHistory)
            df2 = pd.DataFrame(
                {"time": stockHistory['timestamp'], ticker: stockHistory['indicators']['quote'][0]['close']})
            df2['date'] = pd.to_datetime(df2['time'], unit='s')
            df2 = df2.drop(['time'], axis=1)
            df2 = df2.set_index(['date'])
            print(df2)
            return df2


def stockAlloc(stocklist, total):
    if True:
        pass
    else:
        df = pd.DataFrame(columns=['date'])
        df.set_index('date', inplace=True)
        print(type(df))
        for ticker in stocklist:
            df2 = getStockHistory(ticker)
            # NOTE debug
            # print(type(df2))
            df = pd.merge(df, df2, how="outer", on="date")

        mu = expected_returns.mean_historical_return(df)
        S = risk_models.sample_cov(df)
        ef = EfficientFrontier(mu, S)
        raw_weights = ef.max_sharpe()
        weights = ef.clean_weights()

        latest_prices = get_latest_prices(df)

        da = DiscreteAllocation(weights, latest_prices, total)
        allocation, leftover = da.lp_portfolio()
        used = total - float(leftover)
        lp = latest_prices.to_dict()
        stocks = []
        for stock in allocation:
            newlist = [stock, int(allocation[stock]),
                    "{:.2f}".format(lp[stock] * allocation[stock])]
            stocks.append(newlist)
        return(stocks, "{:.2f}".format(used))

# NOTE: debugging
# print(getStockHistory("AAPL"))

# print(getStockHistory2("AAPL"))
