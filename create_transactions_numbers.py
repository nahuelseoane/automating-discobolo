import re

excel_file = "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"


def extract_operation_number(description):
    """Extracts the transaction number from 'Descripción'."""
    match = re.search(r'CRED\.TRF\.\d{2}/\d{2}-C\.(\d+)', description)
    if match:
        return match.group(1)  # ✅ Extracted transaction number
    return None  # ✅ Return None if no match


# ✅ Apply function to extract operation numbers
df_bank["Nro operacion"] = df_bank["Descripción"].apply(
    lambda x: extract_operation_number(str(x)))

# ✅ Check results
print(df_bank[["Descripción", "Nro operacion"]].head())
