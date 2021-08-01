import gspread

gc = gspread.service_account(filename='ticker_analysis/stock-screen-sheet.json')
sh = gc.open_by_key('1fTqUZaEs4QuoWeNrpifPBLc5U6Ltm0OCxDMD9CuGR8c')
worksheet = sh.sheet1

results = worksheet.col_values(1)

print (results)

