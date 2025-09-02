def run_sytech_automation():
    import time
    import os
    from shutil import which

    import pandas as pd
    from selenium import webdriver
    from selenium.webdriver.common.by import By

    from discobolo.config.config import (
        PAYMENTS_PATH,
        SHEET_NAME,
        SYTECH_PASSWORD,
        SYTECH_USER,
        TRANSFER_FILE,
        URL_SYTECH_MAIN,
        YEAR,
    )
    from discobolo.scripts.extra_functions import filter_positive_payments
    from discobolo.scripts.payment_load_function import payment_load

    PAYMENTS_PATH = os.path.abspath(PAYMENTS_PATH)
    TRANSFER_FILE = os.path.abspath(TRANSFER_FILE)

    df, df_filtered = filter_positive_payments(TRANSFER_FILE, SHEET_NAME)

    if df_filtered["Sytech"].eq("Si").all():
        print("   👌 All payments loaded. No need to enter into Sytech.")
        return

    remaining = df_filtered["Sytech"].ne("Si").sum()
    print(f"   ⬆️ Loading {remaining} payments. Proceed with Sytech process.")

    main_concepts = ["CUOTA", "TENIS", "ESCUELITA"]
    df_filtered["Concepto_grouped"] = df_filtered["Concepto"].where(
        df_filtered["Concepto"].isin(main_concepts), "OTROS"
    )
    concept_counts = df_filtered["Concepto_grouped"].value_counts()
    concept_counts_dict = concept_counts.to_dict()

    print(
        "   🔢 Counting concepts:\n",
        f"   🔸Total: {len(df_filtered)}\n",
        f"   🔸Cuota: {concept_counts_dict.get('CUOTA')}\n",
        f"   🔸Tenis: {concept_counts_dict.get('TENIS')}\n",
        f"   🔸Escuelita: {concept_counts_dict.get('ESCUELITA')}\n",
        f"   🔸Otros: {concept_counts_dict.get('OTROS')}\n",
    )

    # kill leftovers
    os.system("pkill -f chromedriver >/dev/null 2>&1 || true")
    os.system("pkill -f 'chrome.*discobolo-chrome-' >/dev/null 2>&1 || true")

    # Ensure runtime dir (Chrome sandbox needs 0700)
    os.environ.setdefault("XDG_RUNTIME_DIR", f"/tmp/runtime-{os.getuid()}")
    os.makedirs(os.environ["XDG_RUNTIME_DIR"], exist_ok=True)
    os.chmod(os.environ["XDG_RUNTIME_DIR"], 0o700)

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": PAYMENTS_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,
        "profile.default_content_settings.popups": 0,
        "safebrowsing.enabled": True,
        "profile.default_content_setting_values.notifications": 2,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    # Headless-safe flags
    chrome_options.add_argument("--headless=new")
    chrome_options.add_argument("--remote-debugging-pipe")
    chrome_options.add_argument("--window-size=1920,1080")
    chrome_options.add_argument("--disable-gpu")
    chrome_options.add_argument("--disable-dev-shm-usage")
    chrome_options.add_argument("--no-sandbox")
    chrome_options.add_argument("--disable-extensions")
    chrome_options.add_argument("--disable-popup-blocking")
    
    # Prefer system Chrome/Chromium (like you did for transfers)
    binary = which("google-chrome") or which("chromium-browser") or which("chromium")
    if binary:
        chrome_options.binary_location = binary

    driver = webdriver.Chrome(options=chrome_options)

    # Enable downloads (new CDP, with fallback)
    try:
        driver.execute_cdp_cmd(
            "Browser.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": PAYMENTS_PATH},
        )
    except Exception:
        driver.execute_cdp_cmd(
            "Page.setDownloadBehavior",
            {"behavior": "allow", "downloadPath": PAYMENTS_PATH},
        )

    driver.get(URL_SYTECH_MAIN)
    time.sleep(3)

    username_input = driver.find_element(By.ID, "user_name")
    password_input = driver.find_element(By.ID, "user_password")
    login_button = driver.find_element(
        By.XPATH,
        '//*[@id="loginModal"]/div/div/div[2]/div/form/div[3]/div[2]/div/div/div[2]/button',
    )

    username_input.send_keys(SYTECH_USER)
    password_input.send_keys(SYTECH_PASSWORD)
    login_button.click()

    payment_load(df_filtered, driver, PAYMENTS_PATH, TRANSFER_FILE, SHEET_NAME, YEAR)

    print("✅ All payments processed successfully!")
    driver.quit()
