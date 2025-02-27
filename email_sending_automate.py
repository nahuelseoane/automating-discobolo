import smtplib
import pandas as pd
from email.mime.multipart import MIMEMultipart
from email.mime.text import MIMEText
from email.mime.application import MIMEApplication
import os

# Email settings
SMTP_SERVER = '${SMTP_SERVER}'  # or your email provider's SMTP server
SMTP_PORT = ${SMTP_PORT}
EMAIL_USER = '${EMAIL_USER}'  # your email address
EMAIL_PASSWORD = '${EMAIL_PASSWORD}'  # your email password

# Define PDF storage folder
pdf_folder = "${BASE_PATH}/${YEAR}/2 Febrero ${YEAR}"
# "G:\.shortcut-targets-by-id\1I8UOrub2whpF3WMcosxM7LPlOgJo6CYk\TRANSFERENCIAS\${YEAR}\2 Febrero ${YEAR}"

# Load Excel file
# excel_file = "/home/jotaene/PROYECTOS/AutoDiscoEmails/recipients.xlsx"
excel_file = "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"
df = pd.read_excel(excel_file)


# Function to send email
def send_email(name, recipient_email, pdf_path):
    if not os.path.exists(pdf_path):  # Check if PDF exists
        print(f"⚠️ Error: PDF not found for {name} ({pdf_path})")
        return False  # Return False if email was not sent

    msg = MIMEMultipart()
    msg['From'], msg['To'], msg['Subject'] = EMAIL_USER, recipient_email, 'Recibo de pago - Transferencia confirmada'

    # Email body text
    body = f'Buenas tardes {name}:\n\nRecibimos su transferencia.\nAdjuntamos el recibo correspondiente.\n\nSaludos!'
    msg.attach(MIMEText(body, 'plain'))

    # Attach PDF
    with open(pdf_path, 'rb') as file:
        part = MIMEApplication(file.read(), Name=os.path.basename(pdf_path))
        part['Content-Disposition'] = f'attachment; filename="{os.path.basename(pdf_path)}"'
        msg.attach(part)

    # Send email
    with smtplib.SMTP_SSL(SMTP_SERVER, SMTP_PORT) as server:
        server.login(EMAIL_USER, EMAIL_PASSWORD)
        server.send_message(msg)

    print(f'Email sent to {name} ({recipient_email}) ✅')
    return True  # Return True if email was successfully sent


# Loop through each recipient and send the email
for index, row in df.iterrows():
    if row['Sent'] == "Yes":  # Skip emails already sent
        print(f"🔃 Skipping {row['Name']} - Email already sent.")
        continue

    name, email, pdf_filename = row['Name'], row['Email'], row['PDF_File']
    # Construct full PDF path
    pdf_path = os.path.join(pdf_folder, pdf_filename)

    if send_email(name, email, pdf_path):  # If email was sent successfully
        df.at[index, "Sent"] = "Yes"  # Mark email as sent in DataFrame

# Save updated Excel file
df.to_excel(excel_file, index=False)
print("🎉Emails sent successfully!")
