import os
import time

from discobolo.config.config import BANK_DOWNLOAD_PATH

TARGET_EXTENSION = ".xlsx"


def run_transfers_renaming():
    time.sleep(2)
    files = [
        f
        for f in os.listdir(BANK_DOWNLOAD_PATH)
        if f.endswith(TARGET_EXTENSION) and not f.endswith(".crdownload")
    ]
    if files:
        try:
            files = sorted(
                os.listdir(BANK_DOWNLOAD_PATH),
                key=lambda f: os.path.getctime(os.path.join(BANK_DOWNLOAD_PATH, f)),
                reverse=True,
            )
            time.sleep(1)
            latest_file = files[0]
            original_path = os.path.join(BANK_DOWNLOAD_PATH, latest_file)

            new_filename = "movimientos_banco.xlsx"
            new_path = os.path.join(BANK_DOWNLOAD_PATH, new_filename)

            os.rename(original_path, new_path)
            print(f"✅ File renamed to: {new_filename}")

        except Exception as e:
            print(f"❌ Problem while changing file name: {e}")
    else:
        print("❌ No files found in the download folder.")


if __name__ == "__main__":
    run_transfers_renaming()
