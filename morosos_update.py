import pandas as pd
from datetime import datetime
from openpyxl import load_workbook
from openpyxl.styles import Font, PatternFill
from openpyxl.utils import get_column_letter


morosos_daily = "${BASE_PATH}/Morosos/descarga_reporte/rockhopper_R10240.xlsx"
morosos_main = "${BASE_PATH}/Morosos/Morosos ${YEAR}.xlsx"

months_es = {
    "January": "Enero", "February": "Febrero", "March": "Marzo",
    "April": "Abril", "May": "Mayo", "June": "Junio",
    "July": "Julio", "August": "Agosto", "September": "Septiembre",
    "October": "Octubre", "November": "Noviembre", "December": "Diciembre"
}

month_en = datetime.now().strftime("%B")
current_month = months_es[month_en]  # e.g., 'Marzo'
print(current_month)
df_daily = pd.read_excel(morosos_daily, skiprows=5, engine="openpyxl")
wb = load_workbook(morosos_main)

# Checking if actual month sheet exists
try:
    with pd.ExcelFile(morosos_main, engine="openpyxl") as xls:
        sheet_names = xls.sheet_names  # Get all sheet names

    if current_month not in sheet_names:
        print(f"📂 {current_month} sheet not found. Creating it...")

        wb.create_sheet(current_month)  # Create new sheet
        wb.save(morosos_main)

        print(f"✅ {current_month} sheet created successfully.")
    else:
        print(f"✅ {current_month} sheet already exists.")

except FileNotFoundError:
    print("❌ Error: Main Morosos file not found!")


ws = wb[current_month]
columns = [cell.value for cell in ws[1]]

# Modify excel
df_daily = df_daily.drop(columns=['NROCUENTA', 'FECHAULT.MOVDEBITO', 'MONTOULT.MOVDEBITO', 'DESC.ULT.MOVDEBITO',
                         'FECHAULT.MOVCREDITO', 'MONTOULT.MOVCREDITO', 'TELEFONO', 'EMAIL', 'SUCURSALEMISORA'])
df_daily = df_daily.sort_values(by=df_daily.columns[1], ascending=False)
df_daily = df_daily.drop(index=0)
# Reset index
df_daily = df_daily.iloc[1:].reset_index(drop=True)
# df_daily = df_daily.drop(index=0).reset_index(drop=True)
# print(f"📌 Morosos Daily columns: {df_daily.columns.tolist()}")

# Remove 0 or less values
df_daily = df_daily[df_daily.iloc[:, 1] > 0]

# Change 2do column name to 'SALDO'
df_daily.columns.values[1] = "SALDO"

# Open the writer and set the correct engine
with pd.ExcelWriter(morosos_main, engine="openpyxl", mode="a", if_sheet_exists="replace") as writer:
    df_daily.to_excel(writer, sheet_name=current_month, index=False)

    # Access the workbook and the active worksheet
    workbook = writer.book
    worksheet = writer.sheets[current_month]

    # ✔️ Adjusted styling
    header_fill = PatternFill(
        start_color='4DA6D2', end_color='4DA6D2', fill_type='solid')  # Excel-style blue
    header_font = Font(color='FFFFFF', bold=True)  # Bold white text

    # Apply the formatting to each header cell
    for cell in worksheet[1]:
        cell.fill = header_fill
        cell.font = header_font

    # ✔️ Auto-adjust column widths
    for column_cells in worksheet.columns:
        max_length = 0
        column_letter = get_column_letter(column_cells[0].column)
        for cell in column_cells:
            if cell.value is not None:
                max_length = max(max_length, len(str(cell.value)))
        worksheet.column_dimensions[column_letter].width = max_length + 2

    # ✔️ Format second column (balance) as currency
    for row in worksheet.iter_rows(min_row=2, min_col=2, max_col=2):
        for cell in row:
            cell.number_format = '"$"#,##0.00'

print("✅ Changes saved successfully!")
wb.close()
