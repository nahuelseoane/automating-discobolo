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


def creating_backup(backup_dir, file):
    basename = os.path.basename(file)
    filename = basename.split()[0]
    filename = filename[:6].lower()
    backup_file = os.path.join(
        backup_dir, f"{filename}_backup_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    )
    shutil.copyfile(file, backup_file)
    print(f"   ✅ Backup created: {filename}")
    return


creating_backup(backup_dir, transfer_file)
creating_backup(backup_dir, emails_file)
creating_backup(backup_dir, morosos_file)
