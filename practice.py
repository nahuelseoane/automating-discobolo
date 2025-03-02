from filter_payments import update_loaded_status, load_and_filter_payments, extract_operation_number, extract_date, sanitize_filename

# Load the Excel file with payments
month = 'Marzo'
excel_file = "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"
sheet_name = month
df, df_filtered = load_and_filter_payments(excel_file, sheet_name)

for index, row in df_filtered.iterrows():

    user = row['Jefe de Grupo']
    amount = row['Importe']

    print(f"User: {user}")

    fecha_extraida = extract_date(row['Descripción'])
    print(fecha_extraida)
