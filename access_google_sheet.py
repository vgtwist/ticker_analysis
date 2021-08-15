import gspread
from gspread.models import Worksheet

def get_worksheet ():
    gc = gspread.service_account(filename='stock-screen-sheet.json')
    sh = gc.open_by_key('1fTqUZaEs4QuoWeNrpifPBLc5U6Ltm0OCxDMD9CuGR8c')
    return sh.sheet1

def get_symbols_from_sheet():
    worksheet = get_worksheet ()

    results = worksheet.col_values(1)

    return results[1:]

def update_row_to_sheet (row_list):
    worksheet = get_worksheet ()
    worksheet.update(row_list[0], [row_list[1:]])
