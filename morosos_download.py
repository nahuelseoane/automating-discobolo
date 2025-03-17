import os
import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from config import MOROSOS_DOWNLOAD, SYTECH_USER, SYTECH_PASSWORD, R10240, URL_SYTECH_MAIN


chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": MOROSOS_DOWNLOAD,
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
driver.execute_cdp_cmd("Page.setDownloadBehavior", {
    "behavior": "allow",
    "downloadPath": MOROSOS_DOWNLOAD  # ✅ Force Chrome to use the right folder
})

# Open Sytech
driver.get(URL_SYTECH_MAIN)

username_input = driver.find_element(By.ID, "user_name")
password_input = driver.find_element(By.ID, "user_password")
login_button = driver.find_element(
    By.XPATH, '//*[@id="loginModal"]/div/div/div[2]/div/form/div[3]/div[2]/div/div/div[2]/button')

username_input.send_keys(SYTECH_USER)
password_input.send_keys(SYTECH_PASSWORD)
login_button.click()

original_window = driver.current_window_handle
time.sleep(2)
# Close extra tabs
for handle in driver.window_handles:
    if handle != original_window:
        driver.switch_to.window(handle)
        driver.close()
driver.switch_to.window(original_window)
# Go to report
driver.get(R10240)
time.sleep(2)
pantalla_button = driver.find_element(By.ID, 'key_xlsx')
pantalla_button.click()
time.sleep(2)

downloaded = False
timeout = 30
start_time = time.time()

while not downloaded and time.time() - start_time < timeout:
    files = os.listdir(MOROSOS_DOWNLOAD)
    downloading = [f for f in files if f.endswith('.crdownload')]
    if not downloading and any(f.endswith('.xlsx') for f in files):
        downloaded = True
    else:
        time.sleep(2)

if downloaded:
    found_file = None
    wait_seconds = 10  # ⏱ wait max 10 more seconds after 'downloaded' was marked True
    wait_start = time.time()

    while not found_file and time.time() - wait_start < wait_seconds:
        for f in os.listdir(MOROSOS_DOWNLOAD):
            if f == "rockhopper_R10240.xlsx":
                found_file = f
                break
        if not found_file:
            time.sleep(1)

    if found_file:

        old_path = os.path.join(MOROSOS_DOWNLOAD, f)
        new_path = os.path.join(MOROSOS_DOWNLOAD, "reporte_morosos.xlsx")

        if os.path.exists(new_path):
            os.remove(new_path)

        os.rename(old_path, new_path)
    else:
        print("⚠️ Downloaded file not found for renaming.")
else:
    print("❌ Timeout - Download may have failed.")

driver.quit()  # ✅ Fully closes Chrome
time.sleep(1)
