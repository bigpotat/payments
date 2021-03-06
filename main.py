from flask import Flask, request, jsonify
from flask import Flask, request, render_template, flash, redirect, url_for, session, Response
from flask_cors import CORS
import uuid
import datetime
import requests
import json
import bokehDashboard
from getCustomerAccounts import getCustomerAccounts
from stockopt import stockAlloc
from stockOrder import stockOrder
from getBalance import getBalance
from sendsms import sendSMS
from getcustomerdetails import getCustomerDetails
import yfinance as yf
import json
import pandas as pd  # data processing, CSV file I/O (e.g. pd.read_csv)
import os
from bokeh.plotting import figure, ColumnDataSource
from bokeh.models.widgets import Dropdown
from bokeh.io import curdoc
from bokeh.layouts import column
from bokeh.plotting import figure, show, output_file, save
from bokeh.io import output_notebook

from bokeh.models import BooleanFilter, CDSView, Select, Range1d, HoverTool
from bokeh.palettes import Category20
from bokeh.models.formatters import NumeralTickFormatter
from bokeh.plotting import figure
from bokeh.embed import components
from bokeh.plotting import figure
from bokeh.embed import components, json_item

app = Flask(__name__)
app.config['SECRET_KEY'] = 'GjIhOUzLBVs5CJ09j04KWg'


def getRecord(record):
    try:
        recordCount = len(record)
        for i in range(0, recordCount, 1):
            acc = record[i]
            return recordCount
    except KeyError:
        if KeyError == 0:
            recordCount = 1
            return recordCount
        else:
            return 0


@app.route('/signup', methods=["GET", "POST"])
def signup(msg=None):
    if request.method == "POST":
        session['name'] = request.form['name']
        user_id = request.form['userID']
        pin = request.form['PIN']
        account = getCustomerAccounts(user_id, pin)[0]
        if account:
            session['user_id'] = user_id
            session['pin'] = pin
            session['account'] = account
            return redirect('/landing')
        else:
            msg = "Invalid tbank credentials"
            return render_template('signup.html', msg=msg)

    if request.method == "GET":
        session.clear()
        return render_template('signup.html')


@app.route('/landing', methods=["GET", "POST"])
def landing():
    balance = getBalance(session['user_id'],
                         session['pin'], session['account'])
    return render_template('landing.html', balance=balance)


@app.route('/settings', methods=["GET", "POST"])
def settings():
    if request.method == "POST":
        session['newMonthlyInvestment'] = request.form['monthly_investment']
        session['newMonthlyInvestmentMsg'] = "You have changed your monthly investment to $" + session['newMonthlyInvestment']
        return redirect('/home')
    if request.method == "GET":
        return render_template('settings.html')


@app.route('/home', methods=["GET", "POST"])
def home():
    if 'account' not in session:
        return redirect('signup')

    if request.method == 'POST':
        symbol = request.form['symbol']
        session['accountBalance'] = getBalance(session['user_id'], session['pin'], session['account'])
    else:
        symbol = 'AAPL'
        session['accountBalance'] = getBalance(session['user_id'], session['pin'], session['account'])

    serviceName = 'getCustomerStocks'
    userID = session['user_id']
    PIN = session['pin']
    OTP = '999999'
    headerObj = {
        'Header': {
            'serviceName': serviceName,
            'userID': userID,
            'PIN': PIN,
            'OTP': OTP
        }
    }

    final_url = "{0}?Header={1}".format(
        "http://tbankonline.com/SMUtBank_API/Gateway", json.dumps(headerObj))
    response = requests.post(final_url)
    serviceRespHeader = response.json(
    )['Content']['ServiceResponse']['ServiceRespHeader']
    errorCode = serviceRespHeader['GlobalErrorID']

    if errorCode == '010000':
        print("get customer stock is working line 116")
        depository_list = response.json(
        )['Content']['ServiceResponse']['DepositoryList']
        if len(depository_list) == 0:
            print("No record found!")
            print("get customer stock is not working line 121")
        else:
            depository_list = depository_list['Depository']
            recordCount = getRecord(depository_list)
            if recordCount > 1:
                stock_value_list = []
                stock_name_list = []

                for i in range(0, recordCount, 1):
                    depository = depository_list[i]
                    symbol_company = depository['symbol']
                    stock_name_list.append(symbol_company)
                    stock_value_list.append(
                        int(depository['quantity']) * float(depository['price']))
    else:
        print("get customer stock not working line 136")


    serviceName = 'getCustomerDetails'
    headerObj = {
        'Header': {
            'serviceName': serviceName,
            'userID': userID,
            'PIN': PIN,
            'OTP': OTP
        }
    }

    final_url = "{0}?Header={1}".format(
        "http://tbankonline.com/SMUtBank_API/Gateway", json.dumps(headerObj))

    response = requests.post(final_url)

    serviceRespHeader = response.json(
    )['Content']['ServiceResponse']['ServiceRespHeader']

    errorCode = serviceRespHeader['GlobalErrorID']

    if errorCode == '010000':
        CDMCustomer = response.json(
        )['Content']['ServiceResponse']['CDMCustomer']
        phonenumber = CDMCustomer['cellphone']['phoneNumber']
        email = CDMCustomer['profile']['email']
        bankid = CDMCustomer['profile']['bankID']

    stonk = yf.Ticker(symbol)
    hist = stonk.history(period='max')

    # Define constants
    W_PLOT = 1000
    H_PLOT = 400
    TOOLS = 'pan,wheel_zoom,hover,reset'

    VBAR_WIDTH = 0.2
    RED = Category20[7][6]
    GREEN = Category20[5][4]

    BLUE = Category20[3][0]
    BLUE_LIGHT = Category20[3][1]

    ORANGE = Category20[3][2]
    PURPLE = Category20[9][8]
    BROWN = Category20[11][10]

    def get_symbol_df(symbol=None):
        df = pd.DataFrame(hist)[-50:]
        df.reset_index(inplace=True)
        df["Date"] = pd.to_datetime(df["Date"])
        return df

    def plot_stock_price(stock):

        p = figure(plot_width=W_PLOT, plot_height=H_PLOT, tools=TOOLS,
                   title="Stock price", toolbar_location='above')

        inc = stock.data['Close'] > stock.data['Open']
        dec = stock.data['Open'] > stock.data['Close']
        view_inc = CDSView(source=stock, filters=[BooleanFilter(inc)])
        view_dec = CDSView(source=stock, filters=[BooleanFilter(dec)])

        # map dataframe indices to date strings and use as label overrides
        p.xaxis.major_label_overrides = {i+int(stock.data['index'][0]): date.strftime(
            '%b %d') for i, date in enumerate(pd.to_datetime(stock.data["Date"]))}
        p.xaxis.bounds = (stock.data['index'][0], stock.data['index'][-1])

        p.segment(x0='index', x1='index', y0='Low', y1='High',
                  color=RED, source=stock, view=view_inc)
        p.segment(x0='index', x1='index', y0='Low', y1='High',
                  color=GREEN, source=stock, view=view_dec)

        p.vbar(x='index', width=VBAR_WIDTH, top='Open', bottom='Close',
               fill_color=BLUE, line_color=BLUE, source=stock, view=view_inc, name="price")
        p.vbar(x='index', width=VBAR_WIDTH, top='Open', bottom='Close',
               fill_color=RED, line_color=RED, source=stock, view=view_dec, name="price")

        p.legend.location = "top_left"
        p.legend.border_line_alpha = 0
        p.legend.background_fill_alpha = 0
        p.legend.click_policy = "mute"

        p.yaxis.formatter = NumeralTickFormatter(format='$ 0,0[.]000')
        p.x_range.range_padding = 0.05
        p.xaxis.ticker.desired_num_ticks = 40
        p.xaxis.major_label_orientation = 3.14/4

        # Select specific tool for the plot
        price_hover = p.select(dict(type=HoverTool))

        # Choose, which glyphs are active by glyph name
        price_hover.names = ["price"]
        # Creating tooltips
        price_hover.tooltips = [("Datetime", "@Date{%Y-%m-%d}"),
                                ("Open", "@Open{$0,0.00}"),
                                ("Close", "@Close{$0,0.00}"), ("Volume", "@Volume{($ 0.00 a)}")]
        price_hover.formatters = {"Date": 'datetime'}

        return p

    stock = ColumnDataSource(
        data=dict(Date=[], Open=[], Close=[], High=[], Low=[], index=[]))
    df = get_symbol_df(symbol)
    stock.data = stock.from_df(df)
    elements = list()

    # update_plot()
    p_stock = plot_stock_price(stock)

    elements.append(p_stock)

    curdoc().add_root(column(elements))
    curdoc().title = 'Bokeh stocks historical prices'

    script, div = components(p_stock)
    kwargs = {'script': script, 'div': div}

    return render_template('home.html', username=session['name'], stock_value_list=stock_value_list, stock_name_list=stock_name_list, **kwargs)


@app.route('/purchase', methods=["GET", "POST"])
def purchase():
    
    if request.method == "POST":
        monthlyInvestment = float(request.form["monthlyInvestment"])
        riskAppetite = request.form["riskAppetite"]
        stockMap = {"low": ["^GSPC", "T", "VOD", "AA", "IBM"],
                    "medium": ["AAP", "FB", "^DJI", "MSFT", "GOOG"],
                    "high": ["YAHOY", "HRB", "A", "AMZN", "NFLX", "TSLA"]}
        stockList = stockMap[riskAppetite]
        allocation, used = stockAlloc(riskAppetite, monthlyInvestment)
        
        session['stocks'] = allocation
        session['used'] = used
        newBalance = float(getBalance(session['user_id'], session['pin'], session['account'])) - float(used)
        # session['accountBalance'] = round(newBalance,2)
        return render_template('purchase.html', allocation=allocation, used=used, newBalance=newBalance)
    result = creditTransfer(session['account'], '6696', float(session['used']), session['user_id'], session['pin'])
    creditTransfer('7083', '6653', float(session['used']), 'A123456', '211285')
    
    if result == True:
        session['paymentMsg'] = "You have successfully paid $" + session['used'] + " to tInvest"
        sendSMS(session['user_id'], session['pin'], '87534035', session['paymentMsg'])
    for stock in session['stocks']:
        stockOrder('buy', session['user_id'], session['pin'],
                                    session['account'], stock[0], stock[1])
    return redirect('home')

# def purchase_OLD():
#     if request.method == "POST":
#         monthlyInvestment = float(request.form["monthlyInvestment"])
#         riskAppetite = request.form["riskAppetite"]
#         stockMap = {"low": ["^GSPC", "T", "VOD", "AA", "IBM"],
#                     "medium": ["AAP", "FB", "^DJI", "MSFT", "GOOG"],
#                     "high": ["YAHOY", "HRB", "A", "AMZN", "NFLX", "TSLA"]}
#         stockList = stockMap[riskAppetite]
#         allocation, used = stockAlloc(stockList, monthlyInvestment)
#         session['stocks'] = allocation
#         newBalance = float(getBalance(
#             session['user_id'], session['pin'], session['account'])) - float(used)
#         return render_template('purchase.html', allocation=allocation, used=used, newBalance=newBalance)
#     all_stocks_purchased = []
#     for stock in session['stocks']:
#         stock_purchased = stockOrder('buy', session['user_id'], session['pin'],
#                                      session['account'], stock[0], stock[1])
#         if stock_purchased:
#             all_stocks_purchased.append(stock_purchased)
#     if all_stocks_purchased:
#         serviceName = 'getCustomerDetails'
#         headerObj = {
#             'Header': {
#                 'serviceName': serviceName,
#                 'userID': session['user_id'],
#                 'PIN': session['pin'],
#                 'OTP': '999999'
#             }
#         }
#         final_url = "{0}?Header={1}".format(
#             "http://tbankonline.com/SMUtBank_API/Gateway", json.dumps(headerObj))
#         response = requests.post(final_url)
#         serviceRespHeader = response.json(
#         )['Content']['ServiceResponse']['ServiceRespHeader']
#         errorCode = serviceRespHeader['GlobalErrorID']
#         if errorCode == '010000':
#             CDMCustomer = response.json(
#             )['Content']['ServiceResponse']['CDMCustomer']
#             phonenumber = CDMCustomer['cellphone']['phoneNumber']
#         message = "You have just purchased stocks on tbank. Stock purchase order ID: " + \
#             str(stock_purchased)
#         sendSMS(session['user_id'], session['pin'], phonenumber, message)
#     return redirect('home')


@app.route('/')
def index():
    return redirect("home", code=302)


@app.route('/sell', methods=["GET", "POST"])
def sell():
    msg = ""
    if request.method == "POST":
        symbol = request.form['symbol']
        quantity = request.form['quantity']
        if (stockOrder('sell', session['user_id'], session['pin'],
                       session['account'], symbol, quantity)):
            return redirect('home')
        else:
            msg = "Unable to sell"
    return render_template('sell.html', msg=msg, allocation=session['stocks'])

@app.route('/pay', methods=["POST", "GET"])
def pay():
    if request.method == "POST":
        amount = request.form['amount']
        print(session['account'])
        # trim session account to last 4 digits
        # session['account'] = session['account'][-4:]
        print(session['account'])
        if (creditTransfer(session['account'],'', amount, session['user_id'], session['pin'])):
            return "paid successfully"
        else:
            # return unable to pay
            return "unable to pay" 
    if request.method == "GET":
        return render_template('pay.html')

@app.route('/logout', methods=['GET'])
def logout():
    session.pop('user_id', None)
    session.pop('pin', None)
    session.pop('account', None)
    session.pop('stocks', None)
    return redirect('home')

def creditTransfer(accountFrom, accountTo, transactionAmount, userID, PIN):
    #Header
    serviceName = 'creditTransfer'
    userID = userID
    PIN = PIN
    OTP = '999999'
    #Content
    accountFrom = accountFrom
    accountTo = accountTo
    transactionAmount = transactionAmount
    transactionReferenceNumber = '12332'
    narrative = '2'
    headerObj = {
                        'Header': {
                        'serviceName': serviceName,
                        'userID':userID,
                        'PIN': PIN,
                        'OTP': OTP
                        }
                        }
    contentObj = {
                        'Content': {
                        'accountFrom': accountFrom,
                        'accountTo': accountTo,
                        'transactionAmount': transactionAmount,
                        'transactionReferenceNumber': transactionReferenceNumber,
                        'narrative': narrative
                        }
                        }
    final_url="{0}?Header={1}&Content={2}".format("http://tbankonline.com/SMUtBank_API/Gateway",json.dumps(headerObj),json.dumps(contentObj))
    response = requests.post(final_url)
    serviceRespHeader = response.json()['Content']['ServiceResponse']['ServiceRespHeader']
    errorCode = serviceRespHeader['GlobalErrorID']

    if errorCode == '010000':
        ServerResponse = response.json()['Content']['ServiceResponse']
        print("Balance After Transferring ${:.2f} ".format(float(ServerResponse['BalanceAfter']['_content_'])))
        print("Transaction ID: ", ServerResponse['TransactionID']['_content_'])
        print("Balance Before Transferring ${:.2f}".format(float(ServerResponse['BalanceBefore']['_content_'])))
    elif errorCode == '010041':
        print("OTP has expired.\nYou will receiving a SMS")  
    else:
        print(serviceRespHeader['ErrorText'])
    return True

if __name__ == "__main__":
    app.run(port=8000, debug=True)
