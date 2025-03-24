import time
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.common.keys import Keys
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC

driver = webdriver.Chrome()
driver.get("https://web.whatsapp.com/")
# Wait for manual QR code scan
input("🔎 Scan the QR code and press Enter to continue...")

try:
    search_box = WebDriverWait(driver, 20).until(
        EC.presence_of_all_elements_located(
            (By.XPATH, "//div[@contenteditable='true' and @title='Search input textbox']"))
    )
    print("✅ Search box found.")
except Exception as e:
    print(f"❌ Error: Search box not found! {e}")
    driver.quit()
    exit()

contact_name = "Nahuel"
search_box.send_keys(contact_name)
time.sleep(2)
search_box.send_keys(Keys.ENTER)

message_box = driver.find_element(
    "xpath", "//div[@contenteditable='true'][@title='Type a message']")
message = "Hola Nahuel"
message_box.send_keys(message)
message_box.send_keys(Keys.ENTER)

print("✅ Message sent successfully!")
time.sleep(5)
driver.quit()
