import time

from selenium import webdriver
from selenium.webdriver.common.by import By


def sytech_login(url, username, password, download_dir):
    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": download_dir,
    }
    chrome_options.add_experimental_option("prefs", prefs)
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless=new")
    driver = webdriver.Chrome(options=chrome_options)
    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior",
        {
            "behavior": "allow",
            "downloadPath": download_dir,  # ✅ Force Chrome to use the right folder
        },
    )

    # Open Sytech
    driver.get(url)

    username_input = driver.find_element(By.ID, "user_name")
    password_input = driver.find_element(By.ID, "user_password")
    login_button = driver.find_element(
        By.XPATH,
        '//*[@id="loginModal"]/div/div/div[2]/div/form/div[3]/div[2]/div/div/div[2]/button',
    )

    username_input.send_keys(username)
    password_input.send_keys(password)
    login_button.click()

    original_window = driver.current_window_handle
    time.sleep(2)
    # Close extra tabs
    for handle in driver.window_handles:
        if handle != original_window:
            driver.switch_to.window(handle)
            driver.close()
    driver.switch_to.window(original_window)
    return driver
