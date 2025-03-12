import pandas as pd
from openpyxl import load_workbook
from filter_payments import extract_dni, filter_positive_payments

# Load the Excel file with payments
month = 'Marzo'
transfer_file = "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"
emails_file = "${BASE_PATH}/${YEAR}/EmailSocios.xlsx"
sheet_name = month
df, transfer = filter_positive_payments(transfer_file, sheet_name)
df_emails = pd.read_excel(emails_file, sheet_name=sheet_name)

transfer["DNI"] = transfer["Descripción"].apply(extract_dni)

# Merge
df_merged = transfer.merge(
    df_emails[['DNI', 'Jefe de Grupo I']],
    on='DNI',
    how='left'
)

# print(df_merged[["Jefe de Grupo", "DNI"]].head())

# Load the workbook
wb = load_workbook(transfer_file)
ws = wb[sheet_name]

for idx, row in df_merged.iterrows():
    full_name = row['Jefe de Grupo I']
    seq, amount = row['N° Secuencia'], row['Importe']
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=False):
        if row[0].value == seq:  # Assuming is Column A (N° Secuencia)
            sent_cell = row[6]  # Column H (Jefe de Grupo)
            if sent_cell.value is None or sent_cell.value == "":
                sent_cell.value = full_name  # ✅ Update the cell without affecting formatting
                print(f"✅ Jefe de Grupo updated: {seq} - {full_name}.")
                if row[5].value is None or sent_cell.value == "":  # Column 'Concept'
                    if not pd.isna(full_name):
                        if full_name == 'CANFORA, KEVIN' and int(amount) < 20000:
                            row[5].value = 'TENIS'
                            continue
                        row[5].value = 'CUOTA'
                        print(f"✅ Concept updated to 'CUOTA' - {seq}")


# Save the workbook as a new file
wb.save(transfer_file)
wb.close()
print(f"✅ Updated file saved as: {transfer_file}")
