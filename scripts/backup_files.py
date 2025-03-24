import os
import shutil
from datetime import datetime
from config.config import TRANSFER_FILE, EMAILS_FILE, MOROSOS_MAIN, BACKUP_PATH

os.makedirs(BACKUP_PATH, exist_ok=True)  # Ensure backup directory exists


def creating_backup(BACKUP_PATH, file):
    basename = os.path.basename(file)
    filename = basename.split()[0]
    filename = filename[:6].lower()
    backup_file = os.path.join(
        BACKUP_PATH, f"{filename}_backup_{datetime.now().strftime('%Y-%m-%d')}.xlsx"
    )
    shutil.copyfile(file, backup_file)
    print(f"   ✅ Backup created: {filename}")
    return


creating_backup(BACKUP_PATH, TRANSFER_FILE)
creating_backup(BACKUP_PATH, EMAILS_FILE)
creating_backup(BACKUP_PATH, MOROSOS_MAIN)
