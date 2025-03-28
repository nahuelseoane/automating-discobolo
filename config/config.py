import os
from dotenv import load_dotenv
from scripts.extra_functions import select_month

load_dotenv()

# EMAIL SETTINGS
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT", 465))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# PATH SETTINGS
YEAR = os.getenv("YEAR")
MONTH_NUMBER = int(os.getenv("MONTH_NUMBER"))
MONTH = select_month(MONTH_NUMBER)
BASE_PATH = os.getenv("BASE_PATH")

BACKUP_PATH = os.path.join(BASE_PATH, "backups")
EMAILS_FILE = os.path.join(BASE_PATH, YEAR, "emails_socios.xlsx")
PAYMENTS_PATH = os.path.join(BASE_PATH, YEAR, f"{MONTH_NUMBER} {MONTH} {YEAR}")
TRANSFER_FILE = os.path.join(BASE_PATH, YEAR, f"Transferencias {YEAR}.xlsx")
BANK_PATH = os.path.join(BASE_PATH, YEAR, "descarga_banco")
BANK_FILE = os.path.join(BANK_PATH, "movimientos_banco.xlsx")
MOROSOS_PATH = os.path.join(BASE_PATH, "Morosos")
MOROSOS_DOWNLOAD = os.path.join(MOROSOS_PATH, "descarga_reporte")
MOROSOS_REPORT = os.path.join(MOROSOS_DOWNLOAD, "reporte_morosos.xlsx")
MOROSOS_MAIN = os.path.join(MOROSOS_PATH, f"Morosos {YEAR}.xlsx")
RECURRENTES_PATH = os.path.join(BASE_PATH, "Recurrentes")
RECURRENTES_DOWNLOAD = os.path.join(
    RECURRENTES_PATH, "descarga_reporte")
RECURRENTES_REPORT = os.path.join(
    RECURRENTES_DOWNLOAD, "rockhopper_R10246.xlsx")
RECURRENTES_MAIN = os.path.join(RECURRENTES_PATH, f"Recurrentes {YEAR}.xlsx")
R10240 = os.getenv("R10240")
R10246 = os.getenv("R10246")
SHEET_NAME = MONTH

# SYTECH
SYTECH_USER = os.getenv("SYTECH_USER")
SYTECH_PASSWORD = os.getenv("SYTECH_PASSWORD")
URL_SYTECH_COBRANZAS = os.getenv("URL_SYTECH_COBRANZAS")
URL_SYTECH_MAIN = os.getenv("URL_SYTECH_MAIN")

# BANK
URL_BANK_MAIN = os.getenv("URL_BANK_MAIN")
URL_BANK_CUENTAS = os.getenv("URL_BANK_CUENTAS")
BANK_USER = os.getenv("BANK_USER")
BANK_PASSWORD = os.getenv("BANK_PASSWORD")
