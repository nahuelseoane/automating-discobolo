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
├── bin/                         # Main execution scripts
│   ├── run_discobolo_pipeline.sh  # Entry point script
│   ├── automation_pipeline.sh     # Orchestrates full process
├── config/                      # Configuration files
│   ├── config.py
│   └── requirements.txt
├── data/                        # Data storage
├── logs/                        # Log files
├── scripts/                     # Supporting automation scripts
├── discobolo/                   # Python CLI package
│   └── cli.py                   # Main CLI logic
├── venv/                        # Virtual environment
├── pyproject.toml               # CLI tool packaging file
├── README.md


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

### 3️⃣ Install dependencies
```bash
pip install -r config/requirements.txt
pip install --editable .
```

🚀 Using the CLI
After activating your virtual environment, you can use the discobolo command from anywhere inside the environment.

Available commands:
bash
Copy
Edit
discobolo --help
discobolo run                    # Full automation pipeline
discobolo send-emails           # Run only email sending
discobolo update-transfers      # Update Excel with bank transfers
discobolo morosos --download    # Download Morosos report
discobolo morosos --update      # Update Morosos main file
⚠ You must activate the virtual environment first:

bash
Copy
Edit
source venv/bin/activate
📌 You should run commands from inside the project folder to ensure relative paths work correctly.

📥 Configuration via .env
Configure sensitive and dynamic variables in a .env file at the root:

dotenv
Copy
Edit
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
📝 Notes
Don’t commit your .env file — it’s already ignored via .gitignore.

Use config.py to load and centralize environment variables.

Keep all command executions within the project folder for best path resolution.

✅ Author
Made with 💙 by @Nahuelseoane



