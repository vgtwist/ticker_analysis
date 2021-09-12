import gspread
from gspread.models import Worksheet

def get_worksheet (sheetname):
    gc = gspread.service_account(filename='stock-screen-sheet.json')
    sh = gc.open_by_key('1fTqUZaEs4QuoWeNrpifPBLc5U6Ltm0OCxDMD9CuGR8c')
    return sh.worksheet(sheetname)

def get_symbols_from_sheet(sheetname):
    worksheet = get_worksheet (sheetname)

    results = worksheet.col_values(1)

    return results[1:]

def update_row_to_sheet (row_list, sheetname):
    worksheet = get_worksheet (sheetname)
    worksheet.update(row_list[0], [row_list[1:]])
