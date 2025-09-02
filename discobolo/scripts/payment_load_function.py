import os
import time
import traceback
import requests
import pandas as pd
from pathlib import Path
from discobolo.scripts.extra_functions import update_loaded_status, extract_operation_number, extract_date, sanitize_filename
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException
from discobolo.config.config import URL_SYTECH_COBRANZAS

def wait_for_new_pdf(dirpath, before, timeout=40):
    end = time.time() + timeout
    while time.time() < end:
        for p in Path(dirpath).glob("*.pdf"):
            if p.name not in before and not p.name.endswith(".crdownload"):
                s1 = p.stat().st_size
                time.sleep(0.5)
                s2 = p.stat().st_size
                if s1 == s2 and s2 > 0:
                    return str(p)
        time.sleep(0.3)
    return None

def _ensure_on_cobranzas(driver, main_handle, url_cobranzas, timeout=10):
    # Close any extra tabs (e.g., PDF) and switch back to main handle
    for h in list(driver.window_handles):
        if h != main_handle:
            try:
                driver.switch_to.window(h)
                driver.close()
            except Exception:
                pass
    driver.switch_to.window(main_handle)

    # If the search box isn't there, re-navigate
    try:
        WebDriverWait(driver, 2).until(EC.presence_of_element_located((By.ID, "p_cliente")))
        return
    except SelTimeout:
        pass

    driver.get(url_cobranzas)
    WebDriverWait(driver, timeout).until(EC.presence_of_element_located((By.ID, "p_cliente")))

def payment_load(df, driver, download_root, excel_file, sheet_name, year):
    original_window = driver.current_window_handle
    time.sleep(2)
    # Close extra tabs
    for handle in driver.window_handles:
        if handle != original_window:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(original_window)

    # Step 2: Navigate to the payment entry page
    driver.get(URL_SYTECH_COBRANZAS)
    # time.sleep(2)
    WebDriverWait(driver, 10).until(EC.presence_of_element_located((By.ID, "p_cliente")))
    main_sytech_handle = driver.current_window_handle
    for index, row in df.iterrows():
        # 👇 Ensure the page is ready before using it
        try:
            WebDriverWait(driver, 3).until(
                EC.presence_of_element_located((By.ID, "p_cliente"))
            )
        except:
            driver.refresh()
            WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "p_cliente"))
            )
        # Checking if Payment already enter
        user = row["Jefe de Grupo"]
        seq, amount = row['N° Secuencia'], row['Importe']
        concept = row["Concepto"]

        if str(concept).strip().lower() == "deposito":
            print(f"   🔃 Skipping - DEPOSITO - {seq}")
            continue

        if str(row['Sytech']).strip().lower() == "no":
            print(f"   🔃 Skipping {concept} - not to be loaded.")
            continue

        if str(row['Sytech']).strip().lower() == "si":
            # print(f"   🔃 Skipping {user} - Payment already loaded.")
            continue

        if pd.isna(concept):
            print(f"Skipping row, 'Concept' column is empty: {seq}")
            continue

        try:
            # If Concept is not 'CUOTA'
            observations = None
            if concept.strip().lower() != 'cuota':
                observations = user
                user = 'CLUB, DE DEPORTES DISCOBOLO'
                print(
                    f"Column 'Concept' different from 'CUOTA' is: {concept}...")
            print(f"🔎 Searching for client: {user}")

            # Locate the search input field
            search_input = WebDriverWait(driver, 5).until(
                EC.presence_of_element_located((By.ID, "p_cliente"))
            )

            # Clear and enter the client's name
            last_name = user.split()[0]

            search_input.clear()
            search_input.send_keys(last_name)
            time.sleep(2)
            search_input.send_keys(Keys.RETURN)

            selected_client = None
            # Wait for the client profile link to appear
            try:

                # Ensure the table is fully loaded before searching for clients
                WebDriverWait(driver, 10).until(
                    EC.presence_of_element_located(
                        (By.XPATH, "//table[contains(@class, 'rh_ac')]"))
                )

                # New XPath to find all `<tr>` elements that contain clients
                client_rows_xpath = "//table[contains(@class, 'rh_ac')]/tbody/tr[@name]"

                # Wait until at least one client row appears
                client_rows = WebDriverWait(driver, 10).until(
                    EC.presence_of_all_elements_located((By.XPATH, client_rows_xpath)))

                # Loop throw dropdown menu
                for row_element in client_rows:

                    try:
                        client_name = row_element.get_attribute(
                            "name").strip()

                        # Match full name
                        if user.replace(",", "").lower() == client_name.replace(",", "").lower():
                            # print(f"✅ Found correct client: {client_name}")

                            try:
                                # Locate the correct client row
                                selected_client = WebDriverWait(driver, 10).until(
                                    EC.presence_of_element_located(
                                        (By.NAME, user))
                                )

                                # Force scroll to the element
                                driver.execute_script(
                                    "arguments[0].scrollIntoView({block: 'center'})", selected_client)
                                time.sleep(1)
                                driver.execute_script(
                                    "arguments[0].click();", selected_client)

                                time.sleep(3)
                            except Exception as e:
                                print(
                                    f"❌ Error selecting {user}: {str(e)}")

                    except NoSuchElementException:
                        print("⚠️ No <td> found inside row, skipping...")
                        continue

                if not selected_client:
                    print(f"❌ Client '{user}' not found in dropdown! ")
                    continue

            except TimeoutException:
                print(
                    f"❌ Client '{user}' not found! Skipping to the next payment.")
                continue

            # Starting payment process
            cobranza_button = driver.find_element(By.ID, "keyComandoCobranza")
            cobranza_button.click()

            # 1. Fecha imputada
            fecha_imputacion = driver.find_element(By.ID, "p_fecha_imputacion")
            fecha_extraida = extract_date(row['Descripción'], year)
            if fecha_extraida:
                fecha_imputacion.clear()
                fecha_imputacion.send_keys(fecha_extraida)
            else:
                formatted_date = row["Fecha"]
                fecha_imputacion.clear()
                fecha_imputacion.send_keys(formatted_date)
            # 2. Observaciones
            if observations:
                observations = concept + " - " + observations
                observations_camp = driver.find_element(
                    By.ID, "p_observaciones")
                observations_camp.clear()
                observations_camp.send_keys(observations)
            # 3. Tipo
            payment_dropdown = WebDriverWait(driver, 10).until(
                EC.presence_of_element_located((By.ID, "p_operacion_tipo"))
            )
            payment_method = Select(payment_dropdown)
            payment_option = "Transf/Depositos"
            payment_method.select_by_visible_text(payment_option)
            # 4. Cuenta Bancaria
            cuenta_dropdown = Select(driver.find_element(
                By.ID, "p_transf_id_cta_cte"))
            select_cuenta = "BANCO DE LA PROVINCIA DE BUENOS AIRES : 123456"
            cuenta_dropdown.select_by_visible_text(select_cuenta)
            # 5. Nro Operacion
            transaction_number = extract_operation_number(row["Descripción"])

            if not transaction_number:
                print(
                    f"⚠️ No transaction number found for {user}. Skipping payment.")
                continue  # Skip if no transaction number is found
            operation_number = driver.find_element(By.ID, "p_transf_nro")
            operation_number.send_keys(transaction_number)
            # 6. Fecha
            formatted_date = row["Fecha"]
            date_input = driver.find_element(By.ID, "p_transf_fecha_cobro")
            date_input.clear()
            date_input.send_keys(formatted_date)
            time.sleep(1)
            # 7. Amount
            amount_input = driver.find_element(By.ID, "p_transf_monto")
            amount_input.send_keys(str(amount))
            # 8. Tipo Operacion
            operation_type = Select(
                driver.find_element(By.ID, "p_transf_tipo"))
            operation_type.select_by_visible_text("Transferencia")
            # 9. "Agregar" button
            agregar_button = driver.find_element(By.ID, "keyAgregarTransf")
            agregar_button.click()
            before=set(os.listdir(download_root))
            # 10. Grabar Cobranza
            grabar_button = driver.find_element(By.ID, "keyGrabar")
            grabar_button.click()
            time.sleep(4)

            # 11. Pop-up Payment Receipt
            try:
                if len(driver.window_handles) > 1:
                    driver.switch_to.window(driver.window_handles[-1])
                    time.sleep(2)

                    # Optional: print to debug what it opened
                    # print("PDF TAB URL:", driver.current_url)


                # Wait for the actual file to load
                pdf_url = driver.current_url
                try:
                    # Build a cookie jar for requests
                    cookies = {c['name']: c['value'] for c in driver.get_cookies()}
                    r = requests.get(pdf_url, cookies=cookies, timeout=60)
                    r.raise_for_status()

                    # Build the filename
                    base = observations if observations else user
                    safe_base = sanitize_filename(base)
                    new_name = f"{safe_base}_{transaction_number}.pdf"

                    # Save PDF
                    dest_path = os.path.join(download_root, new_name)

                    with open(dest_path, "wb") as f:
                        f.write(r.content)

                    update_loaded_status(excel_file, sheet_name, seq)
                    print(f"  ✅ {user} Payment successfully loaded - {seq} → {new_name}")
                except Exception as e:
                    print(f"❌ Could not download PDF via requests: {e}")
                finally:
                    # Always return to Cobranzas page
                    driver.get(URL_SYTECH_COBRANZAS)
                    WebDriverWait(driver, 10).until(
                        EC.presence_of_element_located((By.ID, "p_cliente"))
                    )

            except Exception as e:
                print(f"❌ Error downloading receipt: {str(e)}")
                print("⚒️ Full error detail:")
                traceback.print_exc()

        except Exception as e:
            print(f"❌ Error processing {user}: {e}")
            driver.refresh()
            time.sleep(1)
