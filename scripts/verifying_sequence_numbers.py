import pandas as pd
from config.config import TRANSFER_FILE, SHEET_NAME

df = pd.read_excel(TRANSFER_FILE, sheet_name=SHEET_NAME)

sequence_column = "N° Secuencia"

df[sequence_column] = pd.to_numeric(df[sequence_column], errors='coerce')
df = df.dropna(subset=[sequence_column])

expected_sequence = list(
    range(int(df[sequence_column].iloc[-1])+1, int(df[sequence_column].iloc[0])))
actual_sequence = df[sequence_column].astype(int).tolist()

missing = sorted(set(expected_sequence) - set(actual_sequence))

if missing:
    print("⚠️ Missing sequence number detected:", missing)
else:
    print("✅ All sequence numbers are continuous.")
