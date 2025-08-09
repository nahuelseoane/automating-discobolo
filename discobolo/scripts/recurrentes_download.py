import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from discobolo.config.config import (
    R10246,
    RECURRENTES_DOWNLOAD,
    SYTECH_PASSWORD,
    SYTECH_USER,
    URL_SYTECH_MAIN,
)
from discobolo.scripts.extra_functions import clean_download_folder
from discobolo.scripts.sytech_login import sytech_login


def run_recurrentes_download():
    try:
        clean_download_folder(RECURRENTES_DOWNLOAD)

        driver = sytech_login(
            URL_SYTECH_MAIN, SYTECH_USER, SYTECH_PASSWORD, RECURRENTES_DOWNLOAD
        )

        # Going to report page
        driver.get(R10246)

        # Tick only "Socios Activos"
        checkbox = driver.find_element(By.ID, "p_chk_simple1")
        checkbox.click()
        time.sleep(1)

        # Clicking download button
        download_btn = driver.find_element(By.ID, "key_xlsx")
        download_btn.click()
        time.sleep(10)
        print("   ✅ Successfully downloaded 'Recurrentes' report.")
    except Exception as e:
        print(f"❌ Error downloading 'Recurrentes' report: {e}")

    finally:
        try:
            driver.get(URL_SYTECH_MAIN)

            wait = WebDriverWait(driver, 10)  # waits up to 10 seconds
            menu_btn = wait.until(EC.element_to_be_clickable((By.ID, "rhMenuBar")))
            menu_btn.click()

            logout_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Salir"]'))
            )
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
