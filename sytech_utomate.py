import os
import requests
import re
import time
import pandas as pd
import traceback
from filter_payments import update_loaded_status, load_and_filter_payments, extract_operation_number, sanitize_filename
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support.ui import Select
from selenium.webdriver.support import expected_conditions as EC
from selenium.common.exceptions import TimeoutException, NoSuchElementException

# Load the Excel file with payments
excel_file = "${BASE_PATH}/${YEAR}/Transferencias ${YEAR}.xlsx"
sheet_name = 'Febrero'
df, df_filtered = load_and_filter_payments(excel_file, sheet_name)


# ✅ Convert to the correct format
df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)
df["Fecha"] = df["Fecha"].dt.strftime("%d/%m/%Y")

# Download path
download_root = "${BASE_PATH}/${YEAR}/2 Febrero ${YEAR}"


# Configure Chrome to autodefine folder
chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_root,
    "download.prompt_for_download": False,  # False - Disable the "Save As" dialog
    "download.directory_upgrade": True,
    # True - Prevent Chrome from opening PDFs
    "plugins.always_open_pdf_externally": True,
    "profile.default_content_setting_values.popups": 0,  # Disable pop-ups
    # Allow automatic downloads
    "profile.default_content_setting_values.automatic_downloads": 1,
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

# Start Chrome and open Sytech
driver = webdriver.Chrome(options=chrome_options)

driver.execute_cdp_cmd("Page.setDownloadBehavior", {
    "behavior": "allow",
    "downloadPath": download_root  # ✅ Force Chrome to use the right folder
})

# Open Sytech
driver.get("${URL_SYTECH_MAIN}")

# Wait for the page to load
time.sleep(3)

# Step 1: Log in (Modify these selectors for your login page)
username_input = driver.find_element(By.ID, "user_name")
password_input = driver.find_element(By.ID, "user_password")
login_button = driver.find_element(
    By.XPATH, '//*[@id="loginModal"]/div/div/div[2]/div/form/div[3]/div[2]/div/div/div[2]/button')

username_input.send_keys("${SYTECH_USER}")
password_input.send_keys("${SYTECH_PASSWORD}")
login_button.click()

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

# Step 3: Loop through each payment in the Excel file
index_2 = 0

for index, row in df_filtered.iterrows():
    # Checking if Payment already enter
    user = row['Jefe de Grupo']
    amount = row['Importe']

    # print(f"DEBUG: User: {user}, Sytech Column Value: '{row['Sytech']}'")
    if str(row['Sytech']).strip().lower() == "yes":
        print(f"🔃 Skipping {user} - Payment already loaded.")
        continue
    # New Index to control loop
    index_2 += 1
    try:
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
                    client_name = row_element.get_attribute("name").strip()

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
                            print(f"❌ Error selecting {user}: {str(e)}")

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

        # 1. Tipo
        tipo_dropdown = Select(
            driver.find_element(By.ID, "p_operacion_tipo"))
        payment_dropdown = WebDriverWait(driver, 10).until(
            EC.presence_of_element_located((By.ID, "p_operacion_tipo"))
        )
        payment_method = Select(payment_dropdown)
        payment_option = "Transf/Depositos"
        payment_method.select_by_visible_text(payment_option)
        # 2. Cuenta Bancaria
        cuenta_dropdown = Select(driver.find_element(
            By.ID, "p_transf_id_cta_cte"))
        select_cuenta = "BANCO DE LA PROVINCIA DE BUENOS AIRES : 123456"
        cuenta_dropdown.select_by_visible_text(select_cuenta)
        # 3. Nro Operacion
        transaction_number = extract_operation_number(row["Descripción"])
        df['Nro Operacion'] = transaction_number

        if not transaction_number:
            print(
                f"⚠️ No transaction number found for {user}. Skipping payment.")
            continue  # Skip if no transaction number is found
        operation_number = driver.find_element(By.ID, "p_transf_nro")
        operation_number.send_keys(transaction_number)
        # 4. Fecha
        formatted_date = row["Fecha"]
        date_input = driver.find_element(By.ID, "p_transf_fecha_cobro")
        date_input.clear()
        date_input.send_keys(formatted_date)
        time.sleep(1)
        # 5. Amount
        amount_input = driver.find_element(By.ID, "p_transf_monto")
        amount_input.send_keys(str(row["Importe"]))
        # 6. Tipo Operacion
        operation_type = Select(
            driver.find_element(By.ID, "p_transf_tipo"))
        operation_type.select_by_visible_text("Transferencia")
        # 7. "Agregar" button
        agregar_button = driver.find_element(By.ID, "keyAgregarTransf")
        agregar_button.click()
        # 8. Grabar Cobranza
        grabar_button = driver.find_element(By.ID, "keyGrabar")
        grabar_button.click()
        time.sleep(8)

        # Pop-up Payment Receipt
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
                latest_file = files[0]
                original_path = os.path.join(download_root, latest_file)

                client_name = user
                sanitized_name = sanitize_filename(client_name)
                new_filename = f"{sanitized_name}.pdf"
                new_path = os.path.join(download_root, new_filename)

                os.rename(original_path, new_path)

                update_loaded_status(df, excel_file, sheet_name, user)
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

            print(f"  ✅ {user} Payment successfully loaded")
        except Exception as e:
            print(f"❌ Error downloading receipt: {str(e)}")
            print("⚒️ Full error detail:")
            traceback.print_exc()

    except Exception as e:
        print(f"❌ Error processing {user}: {e}")
        driver.refresh()
        time.sleep(1)

    # if index_2 >= 2:
    #     break

print("✅ All payments processed successfully!")
