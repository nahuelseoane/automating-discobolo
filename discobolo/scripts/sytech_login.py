import time
import os

from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.support.ui import WebDriverWait
from selenium.webdriver.support import expected_conditions as EC


def create_driver(download_dir):
    download_dir = os.path.abspath(download_dir)
    os.makedirs(download_dir, exist_ok=True)

    opts = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.automatic_downloads": 1,
    }
    opts.add_experimental_option("prefs", prefs)
    # if headless:
    opts.add_argument("--headless=new")
    opts.add_argument("--window-size=1920,1080")
    opts.add_argument("--no-sandbox")
    opts.add_argument("--disable-dev-shm-usage")
    opts.add_argument("--disable-extensions")
    opts.add_argument("--disable-popup-blocking")
    opts.add_argument("--disable-features=BlockInsecureDownloads")
    opts.add_argument("--disable-gpu")
    opts.add_argument("--remote-debugging-pipe")


    return webdriver.Chrome(options=opts)


def sytech_login(driver, url, username, password):
    
    driver.get(url)

    # If logged in
    wait = WebDriverWait(driver, 20)

    wait.until(EC.any_of(
        EC.presence_of_element_located((By.ID, "user_name")),   # login form present
        EC.presence_of_element_located((By.ID, "rhMenuBar")),   # already logged in
    ))

    # already logged in → nothing to do
    if driver.find_elements(By.ID, "rhMenuBar"):
        return


    # Open Sytech
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
        # driver.quit()
        print(f" ❌ Login error: {e}")
        raise

    # Close extra tabs
    original_window = driver.current_window_handle
    time.sleep(2)

    for handle in driver.window_handles:
        if handle != original_window:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(original_window)
    # print("📂 Chrome download dir:", download_dir)
    return driver
