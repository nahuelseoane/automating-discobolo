# 📬 Automating Discobolo - Automated Transfers & Notifications System

Welcome to **Automating Discobolo**, a Python-based automation system built to streamline:
- 💳 Payment data processing
- 💾 Excel updates
- 💌 Email notifications with payment receipts
- 💻 Integration with Sytech payment system

This project is designed to simplify daily tasks and improve traceability for payment management.

---

## 📁 Project Structure

```
automating-discobolo/
├── discobolo/
│   ├── __init__.py
│   ├── cli.py                # entry point for the CLI
│   ├── config/               # all configuration
│   │   └── config.py
│   ├── scripts/              # all the automation logic
│   │   ├── backup_files.py
│   │   ├── email_sending_automate.py
│   │   └── extra_functions.py
├── pyproject.toml
├── README.md
├── .gitignore

```

---

## ⚙️ Setup Instructions

### 1️⃣ Clone the repository
```bash
git clone https://github.com/YourUsername/automating-discobolo.git
cd automating-discobolo
```

### 2️⃣ Create and activate virtual environment
```bash
python3 -m venv venv
source venv/bin/activate
```

### 3️⃣ Install project and dependencies
```bash
pip install -r config/requirements.txt
pip install --editable .
```

---

## 🚀 Using the CLI

After activating your virtual environment, you can use the `discobolo` command from anywhere inside the environment.

### Available commands:
```bash
discobolo --help
discobolo run                    # Full automation pipeline
discobolo send-emails           # Run only email sending
discobolo update-transfers      # Update Excel with bank transfers
discobolo morosos --download    # Download Morosos report
discobolo morosos --update      # Update Morosos main file
```

> ⚠ You must activate the virtual environment first:
```bash
source venv/bin/activate
```

> 📌 You should run commands from inside the project folder to ensure relative paths work correctly.

---

## 📥 Configuration via `.env`

Configure sensitive and dynamic variables in a `.env` file at the root:
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

# Sytech / Bank login and URLs
SYTECH_USER=your_sytech_user
SYTECH_PASSWORD=your_sytech_password
BANK_USER=your_bank_user
BANK_PASSWORD=your_bank_password
```

---

## 🧩 Chrome Version Requirement

To ensure downloads and headless mode work properly, this project uses:

> ✅ `google-chrome-stable` version **116.0.5845.140-1** (installed via `.deb`)

Using Snap Chromium may cause issues with:
- ❌ `Page.setDownloadBehavior` not working
- ❌ Headless mode throwing `DevToolsActivePort` error

To install the working version:
```bash
wget https://dl.google.com/linux/direct/google-chrome-stable_current_amd64.deb
sudo dpkg -i google-chrome-stable_current_amd64.deb
sudo apt-mark hold google-chrome-stable

---

## 📝 Notes
- Don’t commit your `.env` file — it’s already ignored via `.gitignore`.
- Use `config.py` to load and centralize environment variables.
- Keep all command executions within the project folder for best path resolution.

---

## ✅ Author
Made with 💙 by [@Nahuelseoane](https://github.com/Nahuelseoane)
