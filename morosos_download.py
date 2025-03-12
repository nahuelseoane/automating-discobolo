import os
import time
import pandas as pd
from selenium import webdriver
from selenium.webdriver.common.by import By

r10240 = '${R10240}'
download_root = "${BASE_PATH}/Morosos"

chrome_options = webdriver.ChromeOptions()
prefs = {
    "download.default_directory": download_root,
}
chrome_options.add_experimental_option("prefs", prefs)
chrome_options.add_argument("--start-maximized")
driver = webdriver.Chrome(options=chrome_options)
driver.execute_cdp_cmd("Page.setDownloadBehavior", {
    "behavior": "allow",
    "downloadPath": download_root  # ✅ Force Chrome to use the right folder
})

# Open Sytech
driver.get("${URL_SYTECH_MAIN}")

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
# Go to report
driver.get(r10240)
time.sleep(2)
pantalla_button = driver.find_element(By.ID, 'key_xlsx')
pantalla_button.click()
time.sleep(2)

# try:
#     # ✅ Ensure Chrome has focus
#     driver.execute_script("window.focus();")

#     # ✅ Find the <body> element and click it to focus
#     body_element = driver.find_element(By.TAG_NAME, "body")
#     body_element.click()
#     time.sleep(5)  # Wait for focus

#     driver.execute_script(
#         "document.execCommand('SaveAs', true, 'receipt.pdf');")

# except Exception as e:
#     print(f"❌ Error saving file: {str(e)}")

# Renaming file


# def wait_for_download(directory, timeout=30):
#     """Waits until a file finishes downloading (no .crdownload exists)."""
#     start_time = time.time()
#     while True:
#         files = os.listdir(directory)
#         crdownload_files = [f for f in files if f.endswith(".crdownload")]

#         if not crdownload_files:  # ✅ No .crdownload means it's done
#             print("Download completed!")
#             break

#         if time.time() - start_time > timeout:  # ⏳ Timeout after 30 sec
#             print("Download timed out!")
#             break

#         time.sleep(1)  # Wait a bit and check again


# # Call this after clicking the download button
# wait_for_download(download_root)


files = sorted(os.listdir(download_root), key=lambda f: os.path.getctime(
    os.path.join(download_root, f)), reverse=True)
if files:
    try:
        latest_file = files[0]
        original_path = os.path.join(download_root, latest_file)
        new_filename = "morososDiario.xlsx"
        new_path = os.path.join(download_root, new_filename)

        os.rename(original_path, new_path)
    except Exception as e:
        print(f"❌ Problem while changing file name: {e}")
else:
    print("❌ No files found in the download folder.")


driver.quit()  # ✅ Fully closes Chrome
print("✅ Chrome closed. Moving to the next task...")
time.sleep(1)
