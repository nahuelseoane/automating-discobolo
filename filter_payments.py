import pandas as pd
import re
from openpyxl import load_workbook


def load_and_filter_payments(excel_file, sheet_name):
    """Load excel file and filter payments by 'Cuota' in the 'Concept' column."""
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df_filtered = df[df["Concepto"].str.contains("Cuota", na=False)].copy()

        df_filtered.reset_index(drop=True, inplace=True)
        print(
            f"✅ Loaded {len(df_filtered)} payments from {sheet_name} (Cuotas) only.")

        # Show filtered file
        # print(f"Solo filas con concepto 'Cuotas':\n{df_filtered[["Jefe de Grupo", "Importe", "Concepto"]].head()}")
        return df, df_filtered
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")


def update_loaded_status(df, excel_file, sheet_name, client_name):
    "Mark the 'Cargado' column as 'Yes' after a successful payment."
    try:
        wb = load_workbook(excel_file)

        if sheet_name not in wb.sheetnames:
            print(f"❌ Error: Sheet '{sheet_name}' not found in {excel_file}")
            return

        ws = wb[sheet_name]

        # ✅ Find the correct row for the client
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=False):
            if row[6].value == client_name:  # Assuming is Column G
                sent_cell = row[7]  # Column H (Cargado)

                # ✅ Update the cell without affecting formatting
                sent_cell.value = "Yes"
                print(f"✅ Marked {client_name} as 'Cargado' in Excel.")

        # ✅ Save the file without overwriting sheets or formatting
        wb.save(excel_file)
        wb.close()
        # user = df['Jefe de Grupo']
        # index = df[user == client_name].index
        # if not index.empty:
        #     df.at[index[0], 'Cargado'] = 'Yes'
        #     print(f"✅ Marked {client_name} as 'Cargado' in Excel.")

        # Save the updated Excel file
        # df.to_excel(excel_file, sheet_name=sheet_name, index=False)
        # print(f"✅ Excel file updated: {excel_file}.")
    except Exception as e:
        print(f"❌ Error updating load status: {e}")


def extract_operation_number(description):
    """Extracts the transaction number from 'Descripción'."""
    match = re.search(r'CRED\.TRF\.\d{2}/\d{2}-C\.(\d+)', str(description))

    return match.group(1) if match else None  # ✅ Extracted transaction number
