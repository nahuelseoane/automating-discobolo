import pandas as pd
import re
from openpyxl import load_workbook


def load_and_filter_payments(excel_file, sheet_name):
    """Load excel file and filter payments by 'Cuota' in the 'Concept' column."""
    try:
        df = pd.read_excel(excel_file, sheet_name=sheet_name)
        df_filtered = df[df["Concepto"].str.contains(
            "Cuota", case=False, na=False)].copy()

        df_filtered.reset_index(drop=True, inplace=True)
        print(
            f"✅ Loaded {len(df_filtered)} payments from {sheet_name} (Cuotas) only.")

        return df, df_filtered
    except Exception as e:
        print(f"❌ Error loading Excel file: {e}")


def sanitize_filename(name):
    """Remove invalid characters for filename."""
    return re.sub(r'[\/:*?"<>|,]', '', name)


def update_loaded_status(df, excel_file, sheet_name, client_name):
    "Mark the 'Sytech' column as 'Yes' after a successful payment."
    try:
        wb = load_workbook(excel_file)

        if sheet_name not in wb.sheetnames:
            print(f"❌ Error: Sheet '{sheet_name}' not found in {excel_file}")
            return

        ws = wb[sheet_name]

        # ✅ Find the correct row for the client
        for row in ws.iter_rows(min_row=2, max_row=ws.max_row, values_only=False):
            if row[6].value == client_name:  # Assuming is Column G
                sent_cell = row[7]  # Column H (Sytech)

                # ✅ Update the cell without affecting formatting
                sent_cell.value = "Yes"

        # ✅ Save the file without overwriting sheets or formatting
        wb.save(excel_file)
        wb.close()
    except Exception as e:
        print(f"❌ Error updating load status: {e}")


def extract_operation_number(description):
    """Extracts the transaction number from 'Descripción'."""
    if not description:
        return None

    description = str(description)

    match = re.search(r'[CS]\.(\d+)', description)

    if match:
        return match.group(1)  # ✅ Extracted number or None

    numbers = re.findall(r"\d+", description)
    if numbers:
        return numbers[0]

    return None
