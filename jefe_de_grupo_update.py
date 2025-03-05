import os
import pandas as pd
import shutil
from datetime import datetime
from openpyxl import load_workbook
from filter_payments import extract_dni, update_loaded_status, load_and_filter_payments, extract_operation_number, extract_date, sanitize_filename

# Load the Excel file with payments
month = 'Marzo'
transfer_file = "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"
emails_file = "${BASE_PATH}/${YEAR}/EmailSocios.xlsx"
sheet_name = month
df, transfer = load_and_filter_payments(transfer_file, sheet_name)
df_emails = pd.read_excel(emails_file, sheet_name=sheet_name)

print("Transferencias columns:", transfer.columns.tolist())
print("Emails Socios columns:", df_emails.columns.tolist())

transfer["DNI"] = transfer["Descripción"].apply(extract_dni)
print(transfer[["Descripción", "DNI"]].head())

# Merge
df_merged = transfer.merge(
    df_emails[['DNI', 'Nombre Completo']],
    on='DNI',
    how='left'
)
print("Merged columns:", df_merged.columns.tolist())
# df_merged = df_merged.drop(columns=['Jefe de Grupo'])
print("New Merged columns:", df_merged.columns.tolist())
# df_merged.rename(columns={"Nombre Completo": "Jefe de Grupo"}, inplace=True)

print(df_merged[["Jefe de Grupo", "DNI"]].head())

# Backup the original file
backup_dir = "/home/jotaene/PROYECTOS/AutoDiscoEmails/backups/"
backup_file = os.path.join(
    backup_dir, f"transfer_file_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
)
shutil.copy(transfer_file, backup_file)
print(f"✅ Backup created: {backup_file}")

# Load the workbook
wb = load_workbook(transfer_file)
ws = wb[sheet_name]

for idx, row in df_merged.iterrows():
    full_name = row['Nombre Completo']
    seq = row['N° Secuencia']
    for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=False):
        if row[0].value == seq:  # Assuming is Column A (N° Secuencia)
            sent_cell = row[6]  # Column H (Jefe de Grupo)
            if sent_cell.value is None or sent_cell.value == "":
                sent_cell.value = full_name  # ✅ Update the cell without affecting formatting


# Save the workbook as a new file
# new_file = transfer_file.replace(".xlsx", "_Updated.xlsx")
wb.save(transfer_file)
wb.close()
print(f"✅ Updated file saved as: {transfer_file}")
