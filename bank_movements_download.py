import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from extra_functions import clean_download_folder
from config import URL_BANK_MAIN, BANK_USER, BANK_PASSWORD, BANK_PATH, URL_BANK_CUENTAS

clean_download_folder(BANK_PATH)


def close_modal_if_present(driver, timeout=5):
    try:
        WebDriverWait(driver, timeout).until(
            EC.presence_of_element_located((By.ID, "modal-popup"))
        )
        # x
        # <button aria-disabled="false" type="button" aria-label="Cerrar." class="btn btn-link-primary btn focusMouse"> <svg data-testid="cerrar-icon" width="13px" height="13px" xmlns="http://www.w3.org/2000/svg" class="svg-icon svg-input-white" xmlns:xlink="http://www.w3.org/1999/xlink" viewBox="0 0 13 13" aria-hidden="true"><path xmlns="http://www.w3.org/2000/svg" d="M12.2763 1.9024C12.6472 1.54696 12.6472 0.954113 12.2763 0.598673C11.9271 0.263994 11.3761 0.263994 11.0269 0.598673L7.1186 4.34414C6.76063 4.6872 6.1959 4.6872 5.83793 4.34414L1.92961 0.598672C1.58038 0.263993 1.02944 0.263994 0.680205 0.598673C0.309311 0.954112 0.309312 1.54696 0.680205 1.9024L4.47613 5.54016C4.8563 5.90449 4.8563 6.51218 4.47613 6.87651L0.680204 10.5143C0.309311 10.8697 0.309311 11.4626 0.680205 11.818C1.02944 12.1527 1.58038 12.1527 1.92961 11.818L5.83793 8.07252C6.1959 7.72947 6.76063 7.72947 7.1186 8.07252L11.0269 11.818C11.3761 12.1527 11.9271 12.1527 12.2763 11.818C12.6472 11.4626 12.6472 10.8697 12.2763 10.5143L8.48039 6.87651C8.10022 6.51218 8.10022 5.90449 8.4804 5.54016L12.2763 1.9024Z" fill="svg-input-white"></path></svg></button>
    except Exception as e:
        print("  ✅ No modal popup found. Continuing...")


def get_last_downloaded_file(download_dir):
    files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        return None
    return max(files, key=os.path.getmtime)


chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": BANK_PATH,
    "download.prompt_for_download": False,
    "download.directory_upgrade": True,
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_setting_values.automatic_downloads": 1,
    "profile.default_content_settings.popups": 0,
    "safebrowsing.enabled": True,
    "profile.default_content_setting_value.notifications": 2
}
chrome_options.add_experimental_option("prefs", prefs)

# Force Chrome to open new windows in the same tab
chrome_options.add_argument("--disable-popup-blocking")
chrome_options.add_argument("--disable-features=InfiniteSessionRestore")
chrome_options.add_argument("--disable-features=AutoReload,tab-hover-cards")
chrome_options.add_argument("--force-app-mode")
chrome_options.add_argument("--disable-site-isolation-trials")
chrome_options.add_argument("--new-window")
chrome_options.add_argument("--start-maximized")
chrome_options.add_argument("--safebrowsing-disable-download-protection")
# chrome_options.add_argument("--headless")
# chrome_options.add_argument("--headless=new")

driver = webdriver.Chrome(options=chrome_options)

driver.execute_cdp_cmd("Page.setDownloadBehavior", {
    "behavior": "allow",
    "downloadPath": BANK_PATH
})

try:
    # Main Bank Login Page
    driver.get(URL_BANK_MAIN)
    # User
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.ID, "username"))).send_keys(BANK_USER)
    time.sleep(1)
    # Password
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.ID, "password"))).send_keys(BANK_PASSWORD)
    # Login
    driver.find_element(
        By.XPATH, '/html/body/div[3]/div/div/div/div/div/div[2]/div/main/div/div/div/div[2]/form/div[4]/button[1]').click()

    # Selecting user
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="radioButtonEmpresa0"]')
    )).click()
    # Button 'Continuar'
    driver.find_element(
        By.XPATH, '/html/body/div[3]/div/div/div/div/div/div[2]/div/main/div/div/div[2]/div/div[2]/button').click()
    time.sleep(5)

    # Skipping Model Pop-up
    close_modal_if_present(driver)
    time.sleep(2)

    # Going to 'Cuentas'
    driver.get(URL_BANK_CUENTAS)
    time.sleep(2)

    # Movimientos
    driver.find_element(
        By.XPATH, '/html/body/div[3]/div/div/div/div/div/div[2]/div[2]/main/div/div/div[1]/div[2]/div/div/div[2]/button').click()
    time.sleep(6)

    # Excel download button
    download_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#cuentasMovimientosContext > div > div > div > div > ul > div > div > button.btn.p-0.me-3.btn-icon-primary.btn.focusMouse')
    ))
    driver.execute_script("arguments[0].click();", download_button)
    time.sleep(10)
    # Renaming file
    files = sorted(os.listdir(BANK_PATH), key=lambda f: os.path.getctime(
        os.path.join(BANK_PATH, f)), reverse=True)
    if files:
        try:
            latest_file = files[0]
            original_path = os.path.join(
                BANK_PATH, latest_file)

            new_filename = "movimientos_banco.xlsx"
            new_path = os.path.join(BANK_PATH, new_filename)

            os.rename(original_path, new_path)

        except Exception as e:
            print(f"❌ Problem while changing file name: {e}")
    else:
        print("❌ No files found in the download folder.")
except Exception as e:
    print(f"Error during automation: {e}")

finally:
    try:
        logout_button = driver.find_element(
            By.CSS_SELECTOR, '#root > div > div > div > div > div > div:nth-child(1) > div > header > div > div > div > div.box.col-2.col-md-6 > div > button')
        logout_button.click()
        print("  ✅ Logout successfully")
    except Exception as e:
        print(f"  ⚠️ Logout failed or already logged out. {e}")
driver.quit()
print("  ✅ Selenium closed.")
