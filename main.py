from flask import Flask, request, render_template, url_for
import analyze_ticker
import access_google_sheet
#import requests


app = Flask(__name__)

@app.route("/")
def home():
    kpi = analyze_ticker.get_kpi()
    ww_ind = analyze_ticker.get_wishingwealth_ind()
    return render_template('home.html', kpi = kpi, ww_ind = ww_ind)

@app.route("/market")
def market():
    kpi = analyze_ticker.get_kpi()
    ww_ind = analyze_ticker.get_wishingwealth_ind()
    return render_template('market.html', kpi = kpi, ww_ind = ww_ind)


@app.route("/analyze", methods=['GET', 'POST'])
def analyze():
    if request.method == "POST":
        stock = request.form["stock"]
        stock = stock.upper().strip()           

        if stock != "":
            #response = requests.get ("https://stock-screen-sheet.uk.r.appspot.com/ticker_info?symbol="+stock)
            stockdict = analyze_ticker.get_ticker_details(stock=stock)

            return render_template('analyze.html', rstock = stock, stockdict = stockdict)
        else:            
            return render_template('analyze.html', rstock = "", stockdict = {})        
    else:
        return render_template('analyze.html', rstock = "", stockdict = {})        


@app.route("/about")
def about():
    return render_template('about.html')


@app.route("/ticker_info")
def ticker_info():
    symbol = request.args.get('symbol')
    return analyze_ticker.get_ticker_details(stock=symbol)

@app.route("/update_sheet")
def update_sheet():
    sheetname = request.args.get('sheetname')
    outputtype = request.args.get('type')

    symbol_list = access_google_sheet.get_symbols_from_sheet(sheetname)
    symbol_detail_dict = analyze_ticker.get_ticker_details_multiple(symbol_list)

    if outputtype == 'detail':
        
        worksheet_range_start = 'A'
        worksheet_range_end = 'X'

        header_row = [worksheet_range_start + '1:'+worksheet_range_end + '1'] + list(list(symbol_detail_dict.values())[0].keys())
    else:
        worksheet_range_start = 'A'
        worksheet_range_end = 'O'

        header_row = [worksheet_range_start + '1:'+worksheet_range_end + '1', 'Symbol', 'Price', 'Volume', 'Avg Volume', 'AVWAP High', 'AVWAP Low', 'GT200', 'GT50', 'GT20', 'GT5', 'GT_AVWAP', 'Acc Dist', 'Signal', 'BB Status', 'Score']

    access_google_sheet.update_row_to_sheet (header_row, sheetname)

    sheet_row = 1

    for i in symbol_detail_dict:
        symbol_details = symbol_detail_dict[i]
        sheet_row = sheet_row + 1
        cell_range = worksheet_range_start+str(sheet_row)+':' + worksheet_range_end +str(sheet_row)
        if outputtype == 'detail':

            symbol_detail_list = [cell_range] + list(symbol_details.values())
        else:
            symbol_detail_list = [cell_range, symbol_details['Symbol'], symbol_details['price'], symbol_details['Volume'], symbol_details['Avg Volume'], symbol_details['AVWAP High'], symbol_details['AVWAP Low']]        
            symbol_detail_list.extend ([symbol_details['GT200'], symbol_details['GT50'], symbol_details['GT20'], symbol_details['GT5'], symbol_details['GT_AVWAP'], symbol_details['AD Day'], symbol_details['Signal'], symbol_details['BB Status'], symbol_details['Score']])

        access_google_sheet.update_row_to_sheet (symbol_detail_list, sheetname)

    return 'OK'



if __name__ == '__main__':
    app.run(debug=True)