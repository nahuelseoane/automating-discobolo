import os
import shutil
import tempfile
import time

from selenium import webdriver
from selenium.common.exceptions import NoSuchElementException, TimeoutException
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


def close_modal_if_present(driver, timeout=5):
    posibles_ids = ["modal-popup", "sessionExpireWarning"]
    for modal_id in posibles_ids:
        try:
            WebDriverWait(driver, timeout).until(
                EC.presence_of_element_located((By.ID, modal_id))
            )
            print(f"⚠️ Popup '{modal_id}' visible. Intentando cerrarlo.")

            try:
                close_btn = driver.find_element(
                    By.XPATH,
                    f"//div[@id='{modal_id}']//button[contains(@class, 'close')]",
                )
            except:
                try:
                    close_btn = driver.find_element(
                        By.XPATH,
                        f"//div[@id='{modal_id}']//button[@aria-label='Cerrar.']",
                    )
                except:
                    print(f"❌ Modal button wasn't found: '{modal_id}'")
                    continue

            driver.execute_script("arguments[0].click();", close_btn)
            time.sleep(1)
            print(f"✅ Popup '{modal_id}' closed.")
        except TimeoutException:
            print("Timeout modal")
        except Exception as e:
            print(f"❌ Error closing modal '{modal_id}': {e}")


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


def run_transfers_download():
    clean_download_folder(BANK_PATH)

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": BANK_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_value.notifications": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-features=InfiniteSessionRestore")
    chrome_options.add_argument("--disable-features=AutoReload,tab-hover-cards")
    chrome_options.add_argument("--force-app-mode")
    chrome_options.add_argument("--disable-site-isolation-trials")
    chrome_options.add_argument("--new-window")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--safebrowsing-disable-download-protection")
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--enable-logging")
    chrome_options.add_argument("--v=1")

    temp_user_data_dir = tempfile.mkdtemp()

    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": BANK_PATH}
    )

    try:
        print("   ▶️ Entering bank page.")
        driver.get(URL_BANK_MAIN)
        time.sleep(2)

        WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "username"))
        ).send_keys(BANK_USER)
        time.sleep(1)
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
            login_button.click()
            print("   ✅ Login successful.")
        except Exception:
            print("   ❌ Error login in.")

        def multiple_users():
            choosing_user = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located(
                    (By.XPATH, '//*[@id="radioButtonEmpresa0"]')
                )
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

        # Closing modal if there is one
        close_modal_if_present(driver)
        time.sleep(2)

        # Going to 'cuentas'
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

        click_with_fallback(
            driver,
            [
                "/html/body/div[3]/div/div/div/div/div/div[2]/div[2]/main/div/div/div[1]/div[2]/div/div/div[2]/button",
                "//button[contains(text(), 'Movimientos')]",
                "//button[@type='button' and contains(., 'Movimientos')]",
            ],
            name="Botón 'Movimientos'",
        )

        def ver_mas_movimientos():
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
                    print(
                        "✅ 'Ver más movimientos' btn successfully clicked with Selenium."
                    )
                except:
                    print("⚠️ Selenium could'nt click. Try with JS.")
                    driver.execute_script("arguments[0].click();", mas_movimientos_btn)
                    print("✅ 'Más movimientos' clicked with JS made.")
                time.sleep(2)
            except Exception as e:
                print(f"❌ Error clicking 'Ver más movimientos': {e}")

        ver_mas_movimientos()
        ver_mas_movimientos()

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

    except Exception as e:
        print(f"Error during automation: {e}")

    finally:
        try:
            logout_button = WebDriverWait(driver, 5).until(
                EC.element_to_be_clickable(
                    (
                        By.CSS_SELECTOR,
                        "#root > div > div > div > div > div > div:nth-child(1) > div > header > div > div > div > div.box.col-2.col-md-6 > div > button",
                    )
                )
            )
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
                logout_button = WebDriverWait(driver, 5).until(
                    EC.element_to_be_clickable(
                        (
                            By.CSS_SELECTOR,
                            "#root > div > div > div > div > div > div:nth-child(1) > div > header > div > div > div > div.box.col-2.col-md-6 > div > button",
                        )
                    )
                )
                logout_button.click()
                print("  ✅ Logout successfully")
                shutil.rmtree(temp_user_data_dir)
                driver.quit()
                print("  ✅ Selenium closed.")
            except Exception as e:
                print(f"Second try logout error: {e}")


if __name__ == "__main__":
    run_transfers_download()
