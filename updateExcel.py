import pandas as pd
import os
import shutil
from datetime import datetime

# File paths (update these to match your actual files)
master_file = "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"
bank_file = "${BASE_PATH}/${YEAR}/BankDailyMovements.xlsx"

# Backup directory
backup_dir = "/home/jotaene/PROYECTOS/AutoDiscoEmails/backups/"
os.makedirs(backup_dir, exist_ok=True)  # Ensure backup directory exists

# Backup the master file before modifying
backup_file = os.path.join(
    backup_dir, f"master_backup_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
shutil.copy(master_file, backup_file)
print(f"✅ Backup created: {backup_file}")

# Get current month index (1 = January, 2 = February, ...)
current_month_index = datetime.now().month

# Load the master file and select the correct month's sheet
xls_master = pd.ExcelFile(master_file)
sheet_names = xls_master.sheet_names

# Ensure the sheet for the current month exists
if len(sheet_names) < current_month_index:
    raise ValueError(
        f"❌ No sheet found for month index {current_month_index}. Available sheets: {sheet_names}")

# Select the correct sheet
# Convert 1-based month to 0-based index
current_month_sheet = sheet_names[current_month_index - 1]

df_master_raw = pd.read_excel(master_file, sheet_name=current_month_sheet)

# Print raw data to debug
print("📌 Raw master file first rows:")
# Print first 10 rows to check where headers start
print(df_master_raw.head(10))

# Try skipping rows automatically
# Adjust this number if needed
df_master = pd.read_excel(
    master_file, sheet_name=current_month_sheet, skiprows=2)

# Load the bank's daily transactions, skipping extra headers if necessary
df_bank = pd.read_excel(bank_file, skiprows=1)  # Adjust skiprows if needed

# Normalize column names (remove spaces and lowercase for consistency)
df_bank.columns = df_bank.columns.str.strip().str.lower()

# Rename columns to match master file
df_bank.rename(columns={
    "número secuencia": "N° Secuencia",
    "fecha": "Fecha",
    "descripción extendida": "Descripción",
    "importe": "Importe",
    "saldo": "Saldo"
}, inplace=True)

# Print cleaned column names to debug
print("📌 Cleaned bank file columns:", df_bank.columns.tolist())

print("📌 Master file columns detected:", df_master.columns.tolist())

# Ensure required columns exist
missing_columns = [col for col in ["N° Secuencia", "Fecha",
                                   "Descripción", "Importe", "Saldo"] if col not in df_bank.columns]
if missing_columns:
    raise ValueError(
        f"❌ Missing expected columns: {missing_columns}. Available columns: {df_bank.columns.tolist()}")

# Select only relevant columns
df_bank = df_bank[["N° Secuencia", "Fecha", "Descripción", "Importe", "Saldo"]]

# Convert 'N° Secuencia' to integer (to avoid format issues)
df_master["N° Secuencia"] = df_master["N° Secuencia"].astype(int)
df_bank["N° Secuencia"] = df_bank["N° Secuencia"].astype(int)

# Find the last sequential number in the master file
last_seq = df_master["N° Secuencia"].max()
print(f"📌 Last recorded sequence in master: {last_seq}")

# Filter bank data to get only new transactions
df_new = df_bank[df_bank["N° Secuencia"] > last_seq]

# Check if there are new transactions to add
if df_new.empty:
    print("✅ No new transactions to update.")
else:
    # Append new data to master file
    df_updated = pd.concat([df_master, df_new], ignore_index=True)

    # Save the updated master file with the correct sheet
    with pd.ExcelWriter(master_file, engine='openpyxl', mode='a', if_sheet_exists='replace') as writer:
        df_updated.to_excel(
            writer, sheet_name=current_month_sheet, index=False)

    print(
        f"✅ {len(df_new)} new transactions added successfully to {current_month_sheet}!")
