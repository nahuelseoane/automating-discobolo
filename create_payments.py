import pandas as pd

file_name = "payments.xlsx"

data = {
    "User": ["Daniel Corengia", "Miguel Glaret"],
    "Amount": [70000.00, 62810.00],
    "Description": ["yes", "no"]
}

df = pd.DataFrame(data)

df.to_excel(file_name, index=False)

print(f'✅ {file_name} created successfully!')
