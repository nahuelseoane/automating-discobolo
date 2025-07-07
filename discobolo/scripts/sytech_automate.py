def run_sytech_automation():
    import time

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

    chrome_options = webdriver.ChromeOptions()
    prefs = {
        "download.default_directory": PAYMENTS_PATH,
        "download.prompt_for_download": False,
        "download.directory_upgrade": True,
        "plugins.always_open_pdf_externally": True,
        "profile.default_content_setting_values.popups": 0,
        "profile.default_content_setting_values.automatic_downloads": 1,
    }
    chrome_options.add_experimental_option("prefs", prefs)

    chrome_options.add_argument("--disable-popup-blocking")
    chrome_options.add_argument("--disable-features=InfiniteSessionRestore")
    chrome_options.add_argument("--disable-features=AutoReload,tab-hover-cards")
    chrome_options.add_argument("--force-app-mode")
    chrome_options.add_argument("--disable-site-isolation-trials")
    chrome_options.add_argument("--new-window")
    chrome_options.add_argument("--start-maximized")
    chrome_options.add_argument("--headless=new")

    driver = webdriver.Chrome(options=chrome_options)

    driver.execute_cdp_cmd(
        "Page.setDownloadBehavior", {"behavior": "allow", "downloadPath": PAYMENTS_PATH}
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
