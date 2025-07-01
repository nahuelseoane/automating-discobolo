import os
import time
import shutil
import tempfile
from selenium import webdriver
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC
from scripts.extra_functions import clean_download_folder
from config.config import URL_BANK_MAIN, BANK_USER, BANK_PASSWORD, BANK_PATH, URL_BANK_CUENTAS


clean_download_folder(BANK_PATH)


def close_modal_if_present(driver, timeout=5):
    posibles_ids = ["modal-popup", "sessionExpireWarning"]
    for modal_id in posibles_ids:
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, modal_id))
            )
            print(f"⚠️ Popup '{modal_id}' visible. Intentando cerrarlo.")

            # Trying different options
            try:
                # 1. Btn class "close"
                close_btn = driver.find_element(By.XPATH, f"//div[@id='{modal_id}']//button[contains(@class, 'close')]")
            except:
                try:
                    # 2. Btn with aria-label "Cerrar."
                    close_btn = driver.find_element(By.XPATH, f"//div[@id='{modal_id}']//button[@aria-label='Cerrar.']")
                except:
                    print(f"❌ No se encontró botón para cerrar el modal '{modal_id}'")
                    continue  # next modal

            driver.execute_script("arguments[0].click();", close_btn)
            time.sleep(1)
            print(f"✅ Popup '{modal_id}' cerrado.")
        except TimeoutException:
            print("Timeout modal")
        except Exception as e:
            print(f"❌ Error al cerrar modal '{modal_id}': {e}")

def get_last_downloaded_file(download_dir):
    files = [os.path.join(download_dir, f) for f in os.listdir(download_dir)]
    files = [f for f in files if os.path.isfile(f)]
    if not files:
        return None
    return max(files, key=os.path.getmtime)


def click_with_fallback(driver, xpath_list, timeout=15, name="elemento"):
    for xpath in xpath_list:
        try:
            el = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", el)
            print(f"✅ Clicked '{name}' using xpath: {xpath}")
            return True
        except Exception as e:
            print(
                f"⚠️ No se encontró '{name}' con xpath: {xpath}. Intentando siguiente...")
    print(f"❌ No se pudo hacer click en '{name}' con ningún xpath.")
    return False


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
# Crontab
chrome_options.add_argument("--headless=new")
chrome_options.add_argument("--disable-gpu")
# chrome_options.add_argument('--disable-software-rasterizer')  # problems in WSL
chrome_options.add_argument("--disable-dev-shm-usage")
chrome_options.add_argument("--no-sandbox")
chrome_options.add_argument("--enable-logging")
chrome_options.add_argument("--v=1")
# For better environments handle
# chrome_options.add_argument("--disable-extensions")
# chrome_options.add_argument("--disable-background-networking")
# chrome_options.add_argument("--disable-default-apps")
# chrome_options.add_argument("--disable-sync")
# chrome_options.add_argument("--disable-translate")


# for Crontab
temp_user_data_dir = tempfile.mkdtemp()
# chrome_options.add_argument(f'--user-data-dir={temp_user_data_dir}')

driver = webdriver.Chrome(options=chrome_options)

driver.execute_cdp_cmd("Page.setDownloadBehavior", {
    "behavior": "allow",
    "downloadPath": BANK_PATH
})

try:
    print("   ▶️ Entering bank page.")
    # Main Bank Login Page
    driver.get(URL_BANK_MAIN)
    # Check if page is ready
    print("Document readyState:", driver.execute_script(
        "return document.readyState;"))
    time.sleep(2)

    # USER
    # DEBUG: find username field
    try:
        username_field = driver.find_element(By.ID, "username")
        print("Username field displayed:", username_field.is_displayed())
        print("Username field enabled:", username_field.is_enabled())
    except Exception as e:
        print(f"Couldn't find username field: {e}")
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.ID, "username"))).send_keys(BANK_USER)
    time.sleep(1)
    print("   ✅ Username selected")

    # PASSWORD
    WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.ID, "password"))).send_keys(BANK_PASSWORD)
    print("   ✅ Password selected")

    # LOGIN
    try:
        login_button = WebDriverWait(driver, 10).until(EC.element_to_be_clickable(
            (By.XPATH,
             '/html/body/div[3]/div/div/div/div/div/div[2]/div/main/div/div/div/div[2]/form/div[4]/button[1]')
        ))
        login_button.click()
        print("   ✅ Login successful.")
    except Exception as e:
        # print(f"   ❌ Error login in {e}")
        print("   ❌ Error login in.")

    # Selecting user
    choosing_user = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.XPATH, '//*[@id="radioButtonEmpresa0"]')
    ))
    driver.execute_script("arguments[0].scrollIntoView(true);", choosing_user)
    time.sleep(1)
    choosing_user.click()
    print("   ✅ Selecting user successful.")

    # BUTTON 'Continuar'
    # Wait for the loading disappears
    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.ID, "globalLoading"))
    )

    # First attempt for clicking "Continuar"
    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.XPATH, '/html/body/div[3]/div/div/div/div/div/div[2]/div/main/div/div/div[2]/div/div[2]/button'))
        )
        driver.execute_script("arguments[0].click();", login_btn)
        print("✅ Clicked first 'Continuar' button.")
    except (TimeoutException, NoSuchElementException) as e:
        print("⚠️ Primer botón no encontrado, intentando alternativa...")

        try:
            # Second attempt: other XPATH more generic or alternative
            alt_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Continuar')]"))
            )
            driver.execute_script("arguments[0].click();", alt_btn)
            print("✅ Clicked alternative 'Continuar' button.")
        except Exception as e:
            # print(f"❌ No se pudo hacer click en ningún botón 'Continuar': {e}")
            print("❌ No se pudo hacer click en ningún botón 'Continuar'.")

    # Skipping Model Pop-up
    close_modal_if_present(driver)
    time.sleep(2)

    # Going to 'Cuentas'
    try:
        cuentas_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (By.CSS_SELECTOR, "button.btn-primary.btn.focusMouse"))
        )
        cuentas_btn.click()
    except Exception as e:
        # print(f"Error clicking on 'Cuentas': {e}")
        print("Error clicking on 'Cuentas'")
        # Option 2
        try:
            cuentas_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[.//p[text()='Ver Cuentas']]"))
            )
            cuentas_btn.click()
            print("Second try successful - button 'Cuentas' clicked.")
        except Exception as e:
            # print(f"2do try - Error clicking on 'Cuentas': {e}")
            print("2do try - Error clicking on 'Cuentas'.")
            # Option 3
            driver.get(URL_BANK_CUENTAS)
    time.sleep(2)

  # Movimientos
    click_with_fallback(driver, [
        "/html/body/div[3]/div/div/div/div/div/div[2]/div[2]/main/div/div/div[1]/div[2]/div/div/div[2]/button",
        "//button[contains(text(), 'Movimientos')]",
        "//button[@type='button' and contains(., 'Movimientos')]"
    ], name="Botón 'Movimientos'")
    # with open("debug_movimientos.html", "w", encoding="utf-8") as f:
    #     f.write(driver.page_source)
    #     print("🧪 HTML guardado en debug_movimientos.html")

    # driver.find_element(
    #     By.XPATH, '/html/body/div[3]/div/div/div/div/div/div[2]/div[2]/main/div/div/div[1]/div[2]/div/div/div[2]/button').click()
    # time.sleep(6)

    # Ver Mas Movimientos
    def ver_mas_movimientos():
        try:
            mas_movimientos_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable((By.ID, "verMasElementos")))
            # Check if it isn't disabled
            disabled_attr = mas_movimientos_btn.get_attribute("aria-disabled")
            if disabled_attr == "true":
                raise Exception("Button is disable (aria-disabled=true)")

            # Doing scroll
            driver.execute_script(
                "arguments[0].scrollIntoView({block: 'center'});", mas_movimientos_btn)

            # Trying with Selenium
            try:
                WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable((By.ID, "verMasElementos")))
                mas_movimientos_btn.click()
                print("✅ 'Ver más movimientos' btn successfully clicked with Selenium.")
            except Exception as click_error:
                print("⚠️ Selenium could'nt click. Try with JS.")
                driver.execute_script(
                    "arguments[0].click();", mas_movimientos_btn)
                print("✅ Click with JS made.")
            time.sleep(2)

        except Exception as e:
            print(
                f"❌ 1st try: Failed to click 'Ver más movimientos'. Error: {e}")
            try:
                mas_movimientos_btn = WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located((By.ID, "verMasElementos")))
                mas_movimientos_btn.click()
                print("   ✅'Ver mas movimientos' btn successfully clicked.")
                time.sleep(2)
            except Exception as e:
                try:
                    print(
                        "  2do try to click on 'Mas Movimientos' failed. Trying other option.")
                    mas_movimientos_btn = WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.XPATH, '//*[@id="verMasElementos"]')))
                    mas_movimientos_btn.click()
                    print("   ✅'Ver mas movimientos' btn successfully clicked.")
                    time.sleep(2)
                except Exception as e:
                    print(
                        "3rd try to click on 'Mas Movimientos' failed. Trying other option.")
                    try:
                        mas_movimientos_btn = WebDriverWait(driver, 10).until(
                            EC.presence_of_element_located((By.CLASS_NAME, "btn-icon-primary")))
                        mas_movimientos_btn.click()
                        print("   ✅'Ver mas movimientos' btn successfully clicked.")
                        time.sleep(2)
                    except Exception as e:
                        print(
                            f"  4th try to click on 'Mas Movimientos' failed. Error: {e}")
            return
    # 1st time:
    ver_mas_movimientos()
    # 2nd time:
    ver_mas_movimientos()

    # Excel download button
    download_button = WebDriverWait(driver, 10).until(EC.presence_of_element_located(
        (By.CSS_SELECTOR, '#cuentasMovimientosContext > div > div > div > div > ul > div > div > button.btn.p-0.me-3.btn-icon-primary.btn.focusMouse')
    ))
    driver.execute_script("arguments[0].click();", download_button)
    time.sleep(10)
except Exception as e:
    print(f"Error during automation: {e}")

finally:
    try:
        logout_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((
            By.CSS_SELECTOR, '#root > div > div > div > div > div > div:nth-child(1) > div > header > div > div > div > div.box.col-2.col-md-6 > div > button')))
        logout_button.click()
        print("  ✅ Logout successfully")
        shutil.rmtree(temp_user_data_dir)
        driver.quit()
        print("  ✅ Selenium closed.")
    except Exception as e:
        print(f"  ⚠️ Logout failed or already logged out. {e}")
        try:
            driver.get(URL_BANK_CUENTAS)
            time.sleep(5)
            logout_button = WebDriverWait(driver, 5).until(EC.element_to_be_clickable((
                By.CSS_SELECTOR, '#root > div > div > div > div > div > div:nth-child(1) > div > header > div > div > div > div.box.col-2.col-md-6 > div > button')))
            logout_button.click()
            print("  ✅ Logout successfully")
            shutil.rmtree(temp_user_data_dir)
            driver.quit()
            print("  ✅ Selenium closed.")
        except Exception as e:
            print(f"Second try login out error: {e}")
