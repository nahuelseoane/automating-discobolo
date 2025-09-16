import os
import time

from selenium.common.exceptions import NoSuchElementException, TimeoutException, ElementClickInterceptedException, WebDriverException
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from discobolo.config.config import (
    MOROSOS_DOWNLOAD,
    R10240,
    SYTECH_PASSWORD,
    SYTECH_USER,
    URL_SYTECH_MAIN,
)
from discobolo.scripts.extra_functions import clean_download_folder
from discobolo.scripts.sytech_login import sytech_login, create_driver

MOROSOS_DOWNLOAD = os.path.abspath(MOROSOS_DOWNLOAD)

def session_alive(driver) -> bool:
    try:
        _ = driver.current_url   # cheap ping
        return True
    except Exception:
        return False

def safe_quit(driver):
    try:
        if driver:
            driver.quit()
    except Exception:
        pass
    return None

def logout_if_possible(driver):
    try:
        if not session_alive(driver):
            return
        wait = WebDriverWait(driver, 8)
        # If menu exists, click and logout; otherwise just return
        if driver.find_elements(By.ID, "rhMenuBar"):
            wait.until(EC.element_to_be_clickable((By.ID, "rhMenuBar"))).click()
            wait.until(EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Salir"]'))).click()
            print("  ✅ Logout successfully")
    except Exception:
        # Silent best-effort; we’re shutting down anyway
        pass

def morosos_report_with_click(driver, file):
    try:
        error_attempts = 0
        driver.get(R10240)
        time.sleep(2)
        pantalla_button = driver.find_element(By.ID, "key_xlsx")
        try:
            pantalla_button.click()
        except ElementClickInterceptedException:
            driver.execute_script("arguments[0].click();", pantalla_button)
        time.sleep(2)

        downloaded = False
        timeout = 30
        start_time = time.time()

        while not downloaded and time.time() - start_time < timeout:
            files = os.listdir(file)
            downloading = [f for f in files if f.endswith(".crdownload")]
            if not downloading and any(f.endswith(".xlsx") for f in files):
                downloaded = True
            else:
                time.sleep(2)

        if downloaded:
            found_file = None
            wait_seconds = 10
            wait_start = time.time()

            while not found_file and time.time() - wait_start < wait_seconds:
                for f in os.listdir(file):
                    if f == "rockhopper_R10240.xlsx":
                        found_file = f
                        break
                if not found_file:
                    time.sleep(1)

            # Rename downloaded file
            if found_file:
                old_path = os.path.join(file, f)
                new_path = os.path.join(MOROSOS_DOWNLOAD, "reporte_morosos.xlsx")

                if os.path.exists(new_path):
                    os.remove(new_path)

                os.rename(old_path, new_path)
                print("  ✅ Morosos report successfully downloaded.")
                return
            else:
                print("⚠️ Downloaded file not found for renaming.")
        else:
            print("❌ Timeout - Download may have failed.")
            error_attempts += 1
            if error_attempts <= 2:
                clean_download_folder(MOROSOS_DOWNLOAD)
                morosos_report_with_click(MOROSOS_DOWNLOAD, driver)
            

        
    except Exception as e:
        print(f"❌ General error: {e}")
    finally:
        try:
            driver.get(URL_SYTECH_MAIN)
            wait = WebDriverWait(driver, 10)
            menu_btn = wait.until(EC.element_to_be_clickable((By.ID, "rhMenuBar")))
            menu_btn.click()

            logout_btn = wait.until(
                EC.element_to_be_clickable((By.CSS_SELECTOR, 'a[title="Salir"]'))
            )
            logout_btn.click()

            print("  ✅ Logout successfully")
            try:
                if driver is not None:
                    driver.quit()
            except Exception as e:
                print(f"⚠️ Could not quit driver cleanly: {e}")
            # driver.quit()
            print("   ✅ Selenium closed")
        except TimeoutException as te:
            print(f"❌ Timeout waiting for element: {te}")
        except NoSuchElementException as ne:
            print(f"❌ Element not found: {ne}")
        except Exception as e:
            print(f"❌ General error logging out of Sytech: {e}")

def run_morosos_download():
    attempts, max_attempts = 0,2
    
    while attempts < max_attempts:
        driver = None
        try:
            clean_download_folder(MOROSOS_DOWNLOAD)
            driver = create_driver(MOROSOS_DOWNLOAD)

            sytech_login(
                driver, URL_SYTECH_MAIN, SYTECH_USER, SYTECH_PASSWORD
            )
            
            morosos_report_with_click(driver, MOROSOS_DOWNLOAD)
            return # success

        except KeyboardInterrupt:
            print("⚠️ Interrupted by user.")
            break
        except Exception as e:
            attempts += 1
            print(f"❌ Attempt {attempts} failed: {e}")
        finally:
            # Only try to logout if the session is still alive
            logout_if_possible(driver)
            driver = safe_quit(driver)
