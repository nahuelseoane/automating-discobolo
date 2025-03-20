import os
from dotenv import load_dotenv
from extra_functions import select_month

load_dotenv()

# EMAIL SETTINGS
SMTP_SERVER = os.getenv("SMTP_SERVER")
SMTP_PORT = int(os.getenv("SMTP_PORT"))
EMAIL_USER = os.getenv("EMAIL_USER")
EMAIL_PASSWORD = os.getenv("EMAIL_PASSWORD")

# PATH VARIABLES
YEAR = os.getenv("YEAR")
TRANSFER_FILE = os.getenv("TRANSFER_FILE")
BASE_PATH = os.getenv("BASE_PATH")
MONTH_NUMBER = int(os.getenv("MONTH_NUMBER"))
MONTH = select_month(MONTH_NUMBER)
EMAILS_FILE = f"{BASE_PATH}/{YEAR}/EmailSocios.xlsx"
PAYMENTS_PATH = f"{BASE_PATH}/{YEAR}/{MONTH_NUMBER} {MONTH} {YEAR}"
TRANSFER_FILE = f"{BASE_PATH}/{YEAR}/Transferencias {YEAR}.xlsx"
BANK_PATH = f"{BASE_PATH}/{YEAR}/descarga_banco"
BANK_FILE = f"{BANK_PATH}/movimientos_banco.xlsx"
MOROSOS_DAILY = f"{BASE_PATH}/Morosos/descarga_reporte/reporte_morosos.xlsx"
MOROSOS_MAIN = f"{BASE_PATH}/Morosos/Morosos {YEAR}.xlsx"
MOROSOS_DOWNLOAD = f"{BASE_PATH}/Morosos/descarga_reporte"
R10240 = os.getenv("R10240")
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
