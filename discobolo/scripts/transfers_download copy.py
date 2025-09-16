import os
from pathlib import Path
import time

from selenium import webdriver
from selenium.common.exceptions import (
    NoSuchElementException,
    TimeoutException,
)
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
# BANK_PATH = '/temp/'


def wait_for_downloads(dir_path, before=None, timeout=60):
    """
    Wait until Chrome finishes at least one NEW download in dir_path.
    - `before`: set of filenames present BEFORE triggering the download.
                If None, it will be computed on first call (less strict).
    Returns: str path to the new finished file, or None on timeout.
    """
    dirp = Path(dir_path)
    dirp.mkdir(parents=True, exist_ok=True)

    if before is None:
        before = {p.name for p in dirp.iterdir() if p.is_file()}

    end = time.time() + timeout
    while time.time() < end:
        # ignore temp/partial files
        candidates = [
            p for p in dirp.iterdir()
            if p.is_file()
            and p.suffix not in {".crdownload", ".tmp", ".part"}
            and p.name not in before
        ]
        if candidates:
            # settle check: size must stop changing
            p = max(candidates, key=lambda x: x.stat().st_mtime)
            s1 = p.stat().st_size
            time.sleep(0.5)
            s2 = p.stat().st_size
            if s1 == s2 and s2 > 0:
                return str(p)
        time.sleep(0.25)
    return None

def wait_for_new_file(dir_path, before, suffixes=(".xlsx", ".csv", ".pdf"), timeout=60):
    from pathlib import Path
    import time
    dirp = Path(dir_path)
    dirp.mkdir(parents=True, exist_ok=True)
    end = time.time() + timeout
    while time.time() < end:
        for p in dirp.iterdir():
            if (p.is_file()
                and p.suffix.lower() in suffixes
                and not p.name.endswith(".crdownload")
                and p.name not in before):
                s1 = p.stat().st_size
                time.sleep(0.5)
                s2 = p.stat().st_size
                if s1 == s2 and s2 > 0:
                    return str(p)
        time.sleep(0.25)
    return None

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
            # 1- Try native click
            try:
                el.click()
            except Exception:    
                # 2- Fallback: JS click
                driver.execute_script("arguments[0].click();", el)
            print(f"✅ Clicked '{name}' using xpath: {xpath}")
            return True
        except Exception:
            print(
                f"⚠️ Couldn't be found '{name}' with xpath: {xpath}. Trying next..."
            )
    print(f"❌ Coulnd't be clicked on '{name}' with any xpath.")
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
        "safebrowsing.disable_download_protection": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Headless-safe flags
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--window-size=1920,1080")
    # chrome_options.add_argument("--window-size=1366,900")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--v=1")
    chrome_options.add_argument("--disable-features=BlockInsecureDownloads")

    # Prefer system Chrome/Chromium if present
    binary = which("google-chrome") or which("chromium-browser") or which("chromium")
    if binary:
        chrome_options.binary_location = binary

    driver = None
    try:
        driver = webdriver.Chrome(options=chrome_options)

        # Allow downloads
        # try:
        #     # New CDP
        #     driver.execute_cdp_cmd(
        #         "Browser.setDownloadBehavior", {"behavior": "allow", "downloadPath": BANK_PATH}
        #     )
        # except Exception:
        #     # Old build
        #     driver.execute_cdp_cmd(
        #         "Page.setDownloadBehavior",
        #         {"behavior": "allow", "downloadPath": BANK_PATH}
        #     )

        print("   ▶️ Entering bank page.")
        driver.get(URL_BANK_MAIN)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(BANK_USER)

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
            
            driver.execute_script("arguments[0].click();", login_button)
            print("   ✅ Login successful.")
        except Exception:
            print("   ❌ Error login in.")

        # If there are multiple users
        # multiple_users(driver)

        # driver.get(URL_BANK_CUENTAS)
        time.sleep(2)
    
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
            print("  ✅ Btn 'Cuentas' successfully clicked.")
        except Exception:
            print("Error clicking on 'Cuentas'")
            try:
                cuentas_btn = WebDriverWait(driver, 10).until(
                    EC.element_to_be_clickable(
                        (By.XPATH, "//button[.//p[text()='Ver Cuentas']]")
                    )
                )
                cuentas_btn.click()
                print("  ✅Second try successful - button 'Cuentas' clicked.")
            except Exception:
                print("2do try - Error clicking on 'Cuentas'.")
                driver.get(URL_BANK_CUENTAS)
        time.sleep(2)

        # Btn 'Movimientos'
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

        prev = driver.window_handles[:]

        # Download button
        before = {p.name for p in Path(BANK_PATH).iterdir() if p.is_file()}
        clicked = click_with_fallback(
            driver,
            [
                "//*[@id='cuentasMovimientosContext']//button[contains(@class,'btn-icon-primary')]",
                "//button[contains(., 'Descargar')]",
                "//button[contains(., 'Exportar')]",
                "//button[@aria-label[contains(., 'Descargar')]]",
                "//button[.//i[contains(@class, 'download') or contains(@class, 'bi-download')]]",
            ],
            name="Btn 'Descargar/Exportar'",
        )
        if not clicked:
            raise RuntimeError("Btn 'descargar' couldn't be clicked.")
        

        # Wait for the menu/dropdown to appear (be permissive with selectors)
        try:
            WebDriverWait(driver, 8).until(
                EC.any_of(
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'dropdown') and (.//a or .//button or .//li)]")),
                    EC.visibility_of_element_located((By.XPATH, "//ul[contains(@class,'dropdown') or contains(@class,'menu')]")),
                    EC.visibility_of_element_located((By.XPATH, "//div[contains(@class,'menu') and (.//a or .//button or .//li)]")),
                )
            )
        except TimeoutException:
            # Some UIs open a popover with fixed container; we’ll try clicking Excel directly anyway.
            pass

        # Click the Excel/XLSX option explicitly
        clicked_excel = click_with_fallback(
            driver,
            [
                "//a[contains(., 'Excel')]",
                "//button[contains(., 'Excel')]",
                "//li[contains(., 'Excel')]",
                "//a[contains(., 'XLSX')]",
                "//button[contains(., 'XLSX')]",
                "//li[contains(., 'XLSX')]",
            ],
            name="Opción 'Excel/XLSX'",
        )

        if not clicked_excel:
            raise RuntimeError("Btn 'descargar' clicked_excel couldn't be clicked.")

        # If there truly is no menu and the icon immediately downloads, that's fine:
        # clicked_excel can be False; we'll still wait for the file.

        # Now wait for the new file (strict .xlsx like you prefer)

        print("ℹ️ Waiting for file to appear in:", BANK_PATH)

        try:
            WebDriverWait(driver, 6).until(lambda d: len(d.window_handles) > len(prev))
            if len(driver.window_handles) > len(prev):
                driver.switch_to.window(driver.window_handles[-1])
                print("🔀 Switched to new download tab")
                # Re-allow downloads on the active tab (harmless if redundant)
                try:
                    driver.execute_cdp_cmd("Browser.setDownloadBehavior",
                        {"behavior": "allow", "downloadPath": BANK_PATH, "eventsEnabled": True})
                except Exception:
                    driver.execute_cdp_cmd("Page.setDownloadBehavior",
                        {"behavior": "allow", "downloadPath": BANK_PATH, "eventsEnabled": True})
        except Exception:
            pass
        # 3 Click
        try:
            # If it appears...
            WebDriverWait(driver, 8).until(
                EC.visibility_of_element_located((By.ID, "globalLoading"))
            )
            # ...wait until it disappears
            WebDriverWait(driver, 120).until(
                EC.invisibility_of_element_located((By.ID, "globalLoading"))
            )
        except TimeoutException:
            # Spinner might be too fast or not used — that's fine
            pass

        # Some banks show the final button inside a modal/toast
        close_modal_if_present(driver)  # clear blocking overlays if any

        # Click the final "Descargar archivo" / "Descargar Excel" control
        clicked_final = click_with_fallback(
            driver,
            [
                # Very specific text first
                "//button[contains(., 'Descargar archivo') and not(@disabled) and not(@aria-disabled='true')]",
                "//a[contains(., 'Descargar archivo')]",
                "//div[contains(@class,'modal') or contains(@class,'toast')]//button[contains(., 'Descargar')]",
                "//div[contains(@class,'modal') or contains(@class,'toast')]//a[contains(., 'Descargar')]",

                # More generic fallbacks
                "//button[contains(., 'Descargar') and contains(., 'Excel') and not(@disabled) and not(@aria-disabled='true')]",
                "//a[contains(., 'Descargar') and (contains(., 'Excel') or contains(@href, '.xlsx') or starts-with(@href, 'blob:') or starts-with(@href, 'data:'))]",

                # Any explicit download link inside a modal
                "//div[contains(@class,'modal')]//a[@download]",
            ],
            name="Botón final 'Descargar archivo'",
            timeout=12,
        )

        if not clicked_final:
            raise RuntimeError("Btn 'descargar' clicked_final couldn't be clicked.")


        # new_file = wait_for_downloads(BANK_PATH, before=before, timeout=60)
        new_file = wait_for_new_file(
            BANK_PATH, 
            before=before, 
            suffixes=(".xlsx", ".xls", ".csv", ".pdf"), 
            timeout=60
            )
        if not new_file:
            # Bonus: sometimes a hidden <a download> is present — try triggering any
            for a in driver.find_elements(By.XPATH, "//a[@download]"):
                try:
                    driver.execute_script("arguments[0].click();", a)
                except Exception:
                    pass
            new_file = wait_for_new_file(BANK_PATH, before=before, suffixes=(".xlsx",), timeout=20)

        if not new_file:
            debug = [p.name for p in Path(BANK_PATH).iterdir()]
            raise TimeoutError(f"Download timeout. Folder now has: {debug}")
        
        print("✅ Downloaded:", new_file)

        # if wait_for_downloads(BANK_PATH, timeout=90):
        #     print("  ✅ Download completed")
        # else:
        #     print("  ❌ Download timeout (check selectors / permissions)")

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
