import os
import time
from selenium.webdriver.support.ui import WebDriverWait
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.support import expected_conditions as EC
from scripts.sytech_login import sytech_login
from selenium.webdriver.common.by import By
from scripts.extra_functions import clean_download_folder
from config.config import MOROSOS_DOWNLOAD, SYTECH_USER, SYTECH_PASSWORD, R10240, URL_SYTECH_MAIN


def morosos_report(file):
    # Go to report
    error_attempts = 0
    driver.get(R10240)
    time.sleep(2)
    pantalla_button = driver.find_element(By.ID, 'key_xlsx')
    pantalla_button.click()
    time.sleep(2)

    downloaded = False
    timeout = 30
    start_time = time.time()

    while not downloaded and time.time() - start_time < timeout:
        files = os.listdir(file)
        downloading = [f for f in files if f.endswith('.crdownload')]
        if not downloading and any(f.endswith('.xlsx') for f in files):
            downloaded = True
        else:
            time.sleep(2)

    if downloaded:
        found_file = None
        wait_seconds = 10  # ⏱ wait max 10 more seconds after 'downloaded' was marked True
        wait_start = time.time()

        while not found_file and time.time() - wait_start < wait_seconds:
            for f in os.listdir(file):
                if f == "rockhopper_R10240.xlsx":
                    found_file = f
                    break
            if not found_file:
                time.sleep(1)

        if found_file:

            old_path = os.path.join(file, f)
            new_path = os.path.join(MOROSOS_DOWNLOAD, "reporte_morosos.xlsx")

            if os.path.exists(new_path):
                os.remove(new_path)

            os.rename(old_path, new_path)
            print("  ✅ Morosos report successfully downloaded.")
        else:
            print("⚠️ Downloaded file not found for renaming.")
    else:
        print("❌ Timeout - Download may have failed.")
        error_attempts += 1
        if error_attempts <= 2:
            clean_download_folder(MOROSOS_DOWNLOAD)
            morosos_report(MOROSOS_DOWNLOAD)


try:
    clean_download_folder(MOROSOS_DOWNLOAD)

    driver = sytech_login(URL_SYTECH_MAIN, SYTECH_USER,
                          SYTECH_PASSWORD, MOROSOS_DOWNLOAD)
    morosos_report(MOROSOS_DOWNLOAD)

except Exception as e:
    print(f"❌ Error downloading 'Recurrentes' report: {e}")

finally:
    try:
        driver.get(URL_SYTECH_MAIN)

        wait = WebDriverWait(driver, 10)  # waits up to 10 seconds
        menu_btn = wait.until(
            EC.element_to_be_clickable((By.ID, "rhMenuBar")))
        menu_btn.click()

        logout_btn = wait.until(EC.element_to_be_clickable(
            (By.CSS_SELECTOR, 'a[title="Salir"]')))
        logout_btn.click()

        print("  ✅ Logout successfully")
        driver.quit()
        print("   ✅ Selenium closed")
    except TimeoutException as te:
        print(f"❌ Timeout waiting for element: {te}")
    except NoSuchElementException as ne:
        print(f"❌ Element not found: {ne}")
    except Exception as e:
        print(f"❌ General error logging out of Sytech: {e}")
