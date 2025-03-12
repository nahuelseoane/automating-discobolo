import os
import shutil
from datetime import datetime

# File paths
transfer_file = "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"
emails_file = "${BASE_PATH}/${YEAR}/EmailSocios.xlsx"
morosos_file = "${BASE_PATH}/Morosos/Morosos ${YEAR}.xlsx"

# Backup directory
backup_dir = "${BASE_PATH}/backups"
os.makedirs(backup_dir, exist_ok=True)  # Ensure backup directory exists

# Backup the transfer file
backup_file = os.path.join(
    backup_dir, f"transfer_backup_{datetime.now().strftime('%Y-%m-%d')}.xlsx")
shutil.copyfile(transfer_file, backup_file)
print(f"✅ Backup 1 created: {backup_file}")

# Backup EmailSocios file
backup_file_2 = os.path.join(
    backup_dir, f"emails_backup_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
)
shutil.copyfile(emails_file, backup_file_2)
print(f"✅ Backup 2 created: {backup_file_2}")

# Backup Morosos file
backup_file_3 = os.path.join(
    backup_dir, f"morosos_backup_{datetime.now().strftime('%Y-%m%d')}.xlsx"
)
shutil.copyfile(morosos_file, backup_file_3)
print(f"✅ Backup 3 created: {backup_file_3}")
