import time
import pandas as pd
from filter_payments import load_and_filter_payments, filter_positive_payments, select_month
from selenium import webdriver
from selenium.webdriver.common.by import By
from payment_load_function import payment_load

# Load the Excel file with payments
YEAR = ${YEAR}
month_number = 3
month = select_month(month_number)
sheet_name = month
transfer_file = f"${BASE_PATH}/{YEAR}/Transferencias {YEAR}.xlsx"
df, df_filtered = load_and_filter_payments(transfer_file, sheet_name)
df, df_transfer = filter_positive_payments(transfer_file, sheet_name)

# ✅ Convert to the correct format
df["Fecha"] = pd.to_datetime(df["Fecha"], dayfirst=True)
df["Fecha"] = df["Fecha"].dt.strftime("%d/%m/%Y")

# Download path
download_path = f"${BASE_PATH}/{YEAR}/{month_number} {month} {YEAR}"
download_root = download_path

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


# Step 3: Loop through each payment in the Excel file
payment_load(df_transfer, driver, download_root,
             transfer_file, sheet_name, YEAR)

print("✅ All payments processed successfully!")

driver.quit()
