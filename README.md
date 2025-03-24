# 📬 Automating Discobolo - Automated Transfers & Notifications System

Welcome to **AutoDiscoEmails**, a Python-based automation system built to streamline:
- 💳 Payment data processing
- 💾 Excel updates
- 💌 Email notifications with payment receipts
- 💻 Integration with Sytech payment system

This project is designed to simplify daily tasks and improve traceability for payment management.

---

## 📁 Project Structure

```
automating-discobolo/
├── bin/                         # Main execution scripts
│   ├── run_discobolo_pipeline.sh  # Entry point script
│   ├── automation_pipeline.sh     # Orchestrates full process
├── config/                      # Configuration files
│   ├── config.py                 # Global settings
│   ├── requirements.txt          # Dependencies list
├── data/                        # Data storage
├── logs/                        # Log files
│   ├── cron_env.log              # Environment logs
│   ├── debug_log.txt             # Debugging logs
│   ├── roadmap.log               # Main process log
├── scripts/                     # All automation scripts
│   ├── backup_files.py
│   ├── bank_movements_download.py
│   ├── check_and_remount.sh
│   ├── email_sending_automate.py
│   ├── extra_functions.py
│   ├── jefe_de_grupo_update.py
│   ├── morosos_download.py
│   ├── morosos_update.py
│   ├── payment_load_function.py
│   ├── sytech_automate.py
│   ├── transfer_file_update.py
│   ├── whatsapp_automate.py
├── venv/                        # Virtual environment
├── .gitignore                   # Git ignored files
├── README.md                    # Project documentation

```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YourUsername/AutoDiscoEmails.git
cd AutoDiscoEmails
```

### 2️⃣ Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install dependencies
```bash
pip install -r requirements.txt
```

### 4️⃣ Configure `.env` file
Create a `.env` file in the root folder:

```dotenv
# Email Credentials
EMAIL_USER=your_email@gmail.com
EMAIL_PASSWORD=your_app_password
SMTP_SERVER=${SMTP_SERVER}
SMTP_PORT=${SMTP_PORT}

# Project Configuration
YEAR=${YEAR}
MONTH_NUMBER=3
BASE_PATH=/mnt/g/.../TRANSFERENCIAS
TRANSFER_FILE=Transferencias ${YEAR}.xlsx
```

---

## 🧠 How It Works

### 📤 `email_sending_automate.py`
- Reads Excel file
- Retrieves email from `EmailSocios.xlsx` using DNI match
- Attaches PDF receipt using unique transaction number
- Updates status in Excel (`Cargado` column) and highlights Importe cell

### 🏦 `update_bank_file.py`
- Reads daily bank movements Excel
- Filters only new entries by comparing last sequence number
- Cleans columns and appends new records in correct format to monthly sheet
- Backs up master file automatically

### 🤖 `sytechAutomate.py`
- Launches Chrome, logs in Sytech
- Searches client by last name or DNI
- Enters payment details, saves receipt
- Stores receipt with name format (e.g., `NroOperacion_User.pdf`)

---

## 📥 Download Paths
All receipts are saved automatically to:
```
{BASE_PATH}/{YEAR}/{MONTH_NUMBER} {MONTH} {YEAR}/
```
You can configure this dynamically using `.env`.

---

## 📝 Notes
- Make sure your Google Drive folders are mounted correctly in WSL2.
- Avoid pushing `.env` to GitHub — it's already listed in `.gitignore`.
- Use `config.py` to centralize variables and logic.

---

## 💬 Support
For help or suggestions, open an issue or contact the project maintainer.

---

## ✅ Author
Made with 💙 by [@Nahuelseoane](https://github.com/Nahuelseoane)

