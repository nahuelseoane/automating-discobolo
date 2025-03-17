import os
import time
import traceback
import pandas as pd
from filter_payments import update_loaded_status, extract_operation_number, extract_date, sanitize_filename, extract_deposito
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.webdriver.common.by import By
from selenium.common.exceptions import TimeoutException, NoSuchElementException


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
    driver.get("${URL_SYTECH_COBRANZAS}")
    time.sleep(2)
    for index, row in df.iterrows():
        # Checking if Payment already enter
        user = row["Jefe de Grupo"]
        seq, amount = row['N° Secuencia'], row['Importe']
        concept = row["Concepto"]

        if extract_deposito(row["Descripción"]):
            print(f"   🔃 Skipping - DEPOSITO - {seq}")
            continue

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
            # 10. Grabar Cobranza
            grabar_button = driver.find_element(By.ID, "keyGrabar")
            grabar_button.click()
            time.sleep(8)

            # 11. Pop-up Payment Receipt
            try:
                # Detect if a new tab is open
                WebDriverWait(driver, 5).until(
                    lambda d: len(d.window_handles) > 1)

                try:
                    # ✅ Ensure Chrome has focus
                    driver.execute_script("window.focus();")

                    # ✅ Find the <body> element and click it to focus
                    body_element = driver.find_element(By.TAG_NAME, "body")
                    body_element.click()
                    time.sleep(1)  # Wait for focus

                    driver.execute_script(
                        "document.execCommand('SaveAs', true, 'receipt.pdf');")
                    # print("✅ Executed JavaScript SaveAs command.")

                except Exception as e:
                    print(f"❌ Error saving file: {str(e)}")

                # Renaming file
                files = sorted(os.listdir(download_root), key=lambda f: os.path.getctime(
                    os.path.join(download_root, f)), reverse=True)
                if files:
                    try:
                        latest_file = files[0]
                        original_path = os.path.join(
                            download_root, latest_file)

                        client_name = user
                        sanitized_name = sanitize_filename(client_name)
                        new_filename = f"{sanitized_name}_{transaction_number}.pdf"
                        if observations:
                            new_filename = f"{observations}_{transaction_number}.pdf"
                        new_path = os.path.join(download_root, new_filename)

                        os.rename(original_path, new_path)

                        update_loaded_status(excel_file, sheet_name, seq)
                    except Exception as e:
                        print(f"❌ Problem while changing file name: {e}")
                else:
                    print("❌ No files found in the download folder.")

                # Close receipt window
                if len(driver.window_handles) > 1:
                    # ✅ The last opened tab is usually the PDF
                    pdf_tab = driver.window_handles[-1]
                    driver.switch_to.window(pdf_tab)  # ✅ Switch to the PDF tab
                    driver.close()  # ✅ Close the PDF viewer

                    # ✅ Return to the main Sytech tab
                    driver.switch_to.window(original_window)
                    driver.refresh()
                    time.sleep(1)
                else:
                    print("⚠️ No extra tab detected for PDF.")

                print(f"  ✅ {user} Payment successfully loaded - {seq}")
            except Exception as e:
                print(f"❌ Error downloading receipt: {str(e)}")
                print("⚒️ Full error detail:")
                traceback.print_exc()

        except Exception as e:
            print(f"❌ Error processing {user}: {e}")
            driver.refresh()
            time.sleep(1)
