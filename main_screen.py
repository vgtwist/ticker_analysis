import access_google_sheet
import analyze_ticker


def main():
    symbol_list = access_google_sheet.get_symbols_from_sheet()

    header_row = ['A1:J1', 'Symbol', 'Price', 'Volume', 'Avg Volume', 'GT200', 'GT50', 'GT20', 'GT5', 'AVWAP High', 'AVWAP Low']
    access_google_sheet.update_row_to_sheet (header_row)

    sheet_row = 1

    for i in symbol_list:
        symbol_details = analyze_ticker.get_ticker_details (i)
        sheet_row = sheet_row + 1
        cell_range = 'A'+str(sheet_row)+':J'+str(sheet_row)
        symbol_detail_list = [cell_range, symbol_details['Symbol'], symbol_details['price'], symbol_details['Volume'], symbol_details['Avg Volume']]        
        symbol_detail_list.extend ([symbol_details['GT200'], symbol_details['GT50'], symbol_details['GT20'], symbol_details['GT5'], symbol_details['AVWAP High'], symbol_details['AVWAP Low']])
        access_google_sheet.update_row_to_sheet (symbol_detail_list)

        #print (symbol_detail_list)


if __name__=="__main__":
    main ()
