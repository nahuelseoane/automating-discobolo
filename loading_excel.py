import pandas as pd

# Define data as a dictionary
data = {
    "Name": ["Nahuel", "Juliana", "Lucas", "Micaela"],
    "Email": ["nahuelseoane@gmail.com", "juliana@email.com", "lucas@email.com", "micaela@email.com"],
    "PDF_File": ["Cristina_Lazarte_4-2-25.pdf", "Juliana_Payment.pdf", "Lucas_Payment.pdf", "Micaela_Payment.pdf"]
}

# Convert to DataFrame
df = pd.DataFrame(data)

# Save to Excel
file_path = "/home/jotaene/PROYECTOS/AutoDiscoEmails/recipients.xlsx"
df.to_excel(file_path, index=False)

print(f"✅ Excel file created successfully at: {file_path}")
