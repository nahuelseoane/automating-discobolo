import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def sytech_login(url, username, password, download_dir):
    download_dir = os.path.abspath(download_dir)
    os.makedirs(download_dir, exist_ok=True)
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popups-blocking")
    chrome_options.add_argument("--remote-debugging-pipe")

    driver = webdriver.Chrome(options=chrome_options)

    try:
        driver.execute_cdp_cmd(
            "Browser.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": download_dir,
            },
        )
    except Exception:
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {
                "behavior": "allow",
                "downloadPath": download_dir,  # ✅ Force Chrome to use the right folder
            },
        )

    # Open Sytech
    driver.get(url)

    try:
        username_input = driver.find_element(By.ID, "user_name")
        password_input = driver.find_element(By.ID, "user_password")
        login_button = driver.find_element(
            By.XPATH,
            '//*[@id="loginModal"]/div/div/div[2]/div/form/div[3]/div[2]/div/div/div[2]/button',
        )

        username_input.send_keys(username)
        password_input.send_keys(password)
        login_button.click()
    except Exception as e:
        driver.quit()
        print(f" ❌ Login error: {e}")

    # Close extra tabs
    original_window = driver.current_window_handle
    time.sleep(2)

    for handle in driver.window_handles:
        if handle != original_window:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(original_window)
    return driver
