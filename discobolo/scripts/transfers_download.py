import os
import shutil
import tempfile
import time
import glob

from selenium import webdriver
from selenium.common.exceptions import (
    ElementClickInterceptedException,
    ElementNotInteractableException,
    NoSuchElementException,
    StaleElementReferenceException,
    TimeoutException,
)
from selenium.webdriver.common.action_chains import ActionChains
from selenium.webdriver.common.by import By
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.support.ui import WebDriverWait

from discobolo.config.config import (
    BANK_PASSWORD,
    BANK_PATH,
    BANK_USER,
    URL_BANK_CUENTAS,
    URL_BANK_MAIN,
)
from discobolo.scripts.extra_functions import clean_download_folder
from shutil import which

# Normalize to absolute path
BANK_PATH = os.path.abspath(BANK_PATH)


def wait_for_downloads(dir_path, timeout=60):
    """
    Wait until Chrome has no *.crdownload files and a real file.
    """
    end = time.time() + timeout
    while time.time() < end:
        if not glob.glob(os.path.join(dir_path, "*.crdownload")):
            files = [f for f in os.listdir(dir_path) if not f.endswith(".tmp")]
            if files:
                return True
        time.sleep(0.5)
    return False

def multiple_users(driver):
    choosing_user = WebDriverWait(driver, 10).until(
        EC.presence_of_element_located((By.XPATH, '//*[@id="radioButtonEmpresa0"]'))
    )
    driver.execute_script("arguments[0].scrollIntoView(true);", choosing_user)
    time.sleep(1)
    choosing_user.click()
    print("   ✅ Selecting user successful.")

    WebDriverWait(driver, 20).until(
        EC.invisibility_of_element_located((By.ID, "globalLoading"))
    )
    # Btn 'continuar'
    try:
        login_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable(
                (
                    By.XPATH,
                    "/html/body/div[3]/div/div/div/div/div/div[2]/div/main/div/div/div[2]/div/div[2]/button",
                )
            )
        )
        driver.execute_script("arguments[0].click();", login_btn)
        print("✅ Clicked first 'Continuar' button.")
    except (TimeoutException, NoSuchElementException):
        print("⚠️ Primer botón no encontrado, intentando alternativa...")
        try:
            alt_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.XPATH, "//button[contains(text(), 'Continuar')]")
                )
            )
            driver.execute_script("arguments[0].click();", alt_btn)
            print("✅ Clicked alternative 'Continuar' button.")
        except Exception:
            print("❌ No se pudo hacer click en ningún botón 'Continuar'.")


def close_modal_if_present(driver, timeout=6):
    # IDs & typical selectors
    modal_locators = [
        (By.ID, "modal-popup"),
        (By.ID, "sessionExpireWarning"),
        (By.CSS_SELECTOR, ".modal.show, .box.modal.show"),
    ]
    close_selectors = [
        (By.CSS_SELECTOR, "#modal-popup .btn-close"),
        (By.CSS_SELECTOR, "#modal-popup [data-bs-dismiss='modal']"),
        (By.XPATH, "//div[@id='modal-popup']//button[contains(., 'Cerrar')]"),
        (By.XPATH, "//div[@id='modal-popup']//button[contains(., 'Entendido')]"),
        (By.XPATH, "//div[@id='modal-popup']//button[contains(., 'Aceptar')]"),
        (By.CSS_SELECTOR, ".modal.show .btn-close"),
        (By.CSS_SELECTOR, ".modal.show [data-bs-dismiss='modal']"),
        (
            By.XPATH,
            "//div[contains(@class,'modal') and contains(@class,'show')]//button[contains(., 'Cerrar') or contains(., 'Entendido') or contains(., 'Aceptar')]",
        ),
    ]

    end = time.time() + timeout
    closed_any = False

    while time.time() < end:
        # Is there a visible modal?
        visible_modal = None
        for how, what in modal_locators:
            for el in driver.find_elements(how, what):
                try:
                    if el.is_displayed():
                        visible_modal = el
                        break
                except Exception:
                    pass
            if visible_modal:
                break

        if not visible_modal:
            if closed_any:
                print("✅ Modal cerrado y oculto.")
            return

        print("⚠️ Modal visible. Intentando cerrar…")
        # Trying differents closing modes
        clicked = False
        for how, what in close_selectors:
            for btn in driver.find_elements(how, what):
                try:
                    driver.execute_script("arguments[0].click();", btn)
                    clicked = True
                    closed_any = True
                    break
                except Exception:
                    pass
            if clicked:
                break

        # If there is no btn, try pressing "esc"
        if not clicked:
            try:
                from selenium.webdriver.common.keys import Keys

                driver.switch_to.active_element.send_keys(Keys.ESCAPE)
                closed_any = True
            except Exception:
                pass

        # Wait till it disappears
        try:
            WebDriverWait(driver, 3).until(
                EC.invisibility_of_element_located(
                    (By.CSS_SELECTOR, ".modal.show, #modal-popup")
                )
            )
        except Exception:
            pass

        time.sleep(0.2)


def wait_modal_gone(driver, timeout=6):
    try:
        WebDriverWait(driver, timeout).until(
            EC.invisibility_of_element_located(
                (By.CSS_SELECTOR, ".modal.show, #modal-popup")
            )
        )
    except Exception:
        pass


def click_with_fallback(driver, xpath_list, timeout=15, name="elemento"):
    for xpath in xpath_list:
        try:
            el = WebDriverWait(driver, timeout).until(
                EC.element_to_be_clickable((By.XPATH, xpath))
            )
            driver.execute_script("arguments[0].click();", el)
            print(f"✅ Clicked '{name}' using xpath: {xpath}")
            return True
        except Exception:
            print(
                f"⚠️ No se encontró '{name}' con xpath: {xpath}. Intentando siguiente..."
            )
    print(f"❌ No se pudo hacer click en '{name}' con ningún xpath.")
    return False


def ver_mas_movimientos(driver):
    try:
        mas_movimientos_btn = WebDriverWait(driver, 10).until(
            EC.element_to_be_clickable((By.ID, "verMasElementos"))
        )
        if mas_movimientos_btn.get_attribute("aria-disabled") == "true":
            raise Exception("Button is disable (aria-disabled=true)")
        driver.execute_script(
            "arguments[0].scrollIntoView({block: 'center'});",
            mas_movimientos_btn,
        )

        try:
            WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable((By.ID, "verMasElementos"))
            )
            mas_movimientos_btn.click()
            print("✅ 'Ver más movimientos' btn successfully clicked with Selenium.")
        except:
            print("⚠️ Selenium could'nt click. Try with JS.")
            driver.execute_script("arguments[0].click();", mas_movimientos_btn)
            print("✅ 'Más movimientos' clicked with JS made.")
        time.sleep(2)
    except Exception as e:
        print(f"❌ Error clicking 'Ver más movimientos': {e}")


def run_transfers_download():
    # Ensure download dir and start clean
    os.makedirs(BANK_PATH, exist_ok=True)
    clean_download_folder(BANK_PATH)

    # kill leftovers
    os.system("pkill -f chromedriver >/dev/null 2>&1 || true")
    os.system("pkill -f 'chrome.*discobolo-chrome-' >/dev/null 2>&1 || true")

    # Ensure runtime dir exists
    os.environ.setdefault("XDG_RUNTIME_DIR", f"/tmp/runtime-{os.getuid()}")
    os.makedirs(os.environ["XDG_RUNTIME_DIR"], exist_ok=True)
    os.chmod(os.environ["XDG_RUNTIME_DIR"], 0o700)

    # Build Chrome options
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": BANK_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.notifications": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Headless-safe flags
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--v=1")

    # Prefer system Chrome/Chromium if present
    binary = which("google-chrome") or which("chromium-browser") or which("chromium")
    if binary:
        chrome_options.binary_location = binary

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Allow downloads
        try:
            # New CDP
            driver.execute_cdp_cmd(
                "Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": BANK_PATH}
            )
        except Exception:
            # Old build
            driver.execute_cdp_cmd(
                "Page.setDownloadBehavior",
                {"behavior": "allow", "downloadPath": BANK_PATH}
            )

        print("   ▶️ Entering bank page.")
        driver.get(URL_BANK_MAIN)
        # time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(BANK_USER)
        # time.sleep(1)
        print("   ✅ Username selected")

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "password"))
        ).send_keys(BANK_PASSWORD)
        print("   ✅ Password selected")

        try:
            login_button = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (
                        By.XPATH,
                        "/html/body/div[3]/div/div/div/div/div/div[2]/div/main/div/div/div/div[2]/form/div[4]/button[1]",
                    )
                )
            )
            # login_button.click()
            driver.execute_script("arguments[0].click();", login_button)
            print("   ✅ Login successful.")
        except Exception:
            print("   ❌ Error login in.")

        # If there are multiple users
        # multiple_users(driver)

        # Closing modal if there is one
        close_modal_if_present(driver)
        wait_modal_gone(driver)
        time.sleep(2)

        # Going to 'Cuentas'
        try:
            cuentas_btn = WebDriverWait(driver, 10).until(
                EC.element_to_be_clickable(
                    (By.CSS_SELECTOR, "button.btn-primary.btn.focusMouse")
                )
            )
            cuentas_btn.click()
        except Exception:
            print("Error clicking on 'Cuentas'")
            try:
                cuentas_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[.//p[text()='Ver Cuentas']]")
                    )
                )
                cuentas_btn.click()
                print("Second try successful - button 'Cuentas' clicked.")
            except Exception:
                print("2do try - Error clicking on 'Cuentas'.")
                driver.get(URL_BANK_CUENTAS)
        time.sleep(2)

        # Closing modal if there is one
        close_modal_if_present(driver)
        wait_modal_gone(driver)

        click_with_fallback(
            driver,
            [
                "/html/body/div[3]/div/div/div/div/div/div[2]/div[2]/main/div/div/div[1]/div[2]/div/div/div[2]/button",
                "//button[contains(text(), 'Movimientos')]",
                "//button[@type='button' and contains(., 'Movimientos')]",
            ],
            name="Botón 'Movimientos'",
        )
        close_modal_if_present(driver)
        wait_modal_gone(driver)

        ver_mas_movimientos(driver)
        ver_mas_movimientos(driver)

        close_modal_if_present(driver)
        wait_modal_gone(driver)

        time.sleep(2)

        download_button = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located(
                (
                    By.CSS_SELECTOR,
                    "#cuentasMovimientosContext > div > div > div > div > ul > div > div > button.btn.p-0.me-3.btn-icon-primary.btn.focusMouse",
                )
            )
        )
        driver.execute_script("arguments[0].click();", download_button)
        time.sleep(10)
        if wait_for_downloads(BANK_PATH, timeout=90):
            print("  ✅ Download completed")
        else:
            print("  ❌ Download timeout (check selectors / permissions)")

    except Exception as e:
        print(f"Error during automation: {e}")

    finally:
        try:
            if driver:
                try:
                    close_modal_if_present(driver)
                    wait_modal_gone(driver)
                    logout_button = WebDriverWait(driver, 5).until(
                        EC.element_to_be_clickable(
                            (
                                By.CSS_SELECTOR,
                                "#root > div > div > div > div > div > div:nth-child(1) > div > header > div > div > div > div.box.col-2.col-md-6 > div > button",
                            )
                        )
                    )
                    # logout_button.click()
                    driver.execute_script("arguments[0].click();", logout_button)
                    print("  ✅ Logout successfully")
                except Exception as e:
                    print(f"  ⚠️ Logout failed or already logged out. {e}")
                    try:
                        driver.get(URL_BANK_CUENTAS)
                        time.sleep(5)
                        logout_button = WebDriverWait(driver, 5).until(
                            EC.element_to_be_clickable(
                                (
                                    By.CSS_SELECTOR,
                                    "#root > div > div > div > div > div > div:nth-child(1) > div > header > div > div > div > div.box.col-2.col-md-6 > div > button",
                                )
                            )
                        )
                        # logout_button.click()
                        driver.execute_script("arguments[0].click();", logout_button)
                        print("  ✅ Logout successfully (2nd try)")
                    except Exception as e:
                        print(f"Second try logout error: {e}")
        finally:
            if driver:
                driver.quit()
            print("  ✅ Selenium closed.")


if __name__ == "__main__":
    run_transfers_download()
