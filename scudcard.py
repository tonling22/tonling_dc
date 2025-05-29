def google_search_dcard(query):
    import platform
    import os
    import time
    import logging
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    import undetected_chromedriver as uc

    def get_chrome_path():
        system = platform.system()
        if system == "Windows":
            possible_paths = [
                r"C:\Program Files\Google\Chrome\Application\chrome.exe",
                r"C:\Program Files (x86)\Google\Chrome\Application\chrome.exe",
            ]
            for path in possible_paths:
                if os.path.exists(path):
                    return path
            raise FileNotFoundError("找不到 Chrome 執行檔")
        elif system == "Linux":
            return "/usr/bin/google-chrome"
        else:
            raise NotImplementedError(f"不支援的系統: {system}")

    chrome_path = get_chrome_path()
    options = uc.ChromeOptions()
    options.binary_location = chrome_path
    options.add_argument('--no-sandbox')
    options.add_argument('--disable-dev-shm-usage')
    options.add_argument('--disable-gpu')
    options.add_argument('--log-level=3')

    try:
        driver = uc.Chrome(options=options)
    except Exception as e:
        logging.error(f"Chrome 啟動失敗: {e}")
        return []

    # 使用 site:dcard.tw 限定搜尋範圍到 Dcard
    google_query = f"site:dcard.tw {query}"
    search_url = f"https://www.google.com/search?q={google_query}"
    logging.info(f"前往 Google 搜尋頁: {search_url}")
    driver.get(search_url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'div.g'))
        )
    except Exception as e:
        logging.warning(f"等待搜尋結果超時: {e}")
        driver.quit()
        return []

    time.sleep(2)

    # 取得搜尋結果連結與標題
    results = []
    seen = set()

    # Google 結果通常放在 a 標籤內（有可能在 <h3> 下的 <a>）
    links = driver.find_elements(By.CSS_SELECTOR, 'a')
    for link in links:
        href = link.get_attribute('href')
        if href and "dcard.tw" in href and href not in seen:
            try:
                title = link.text.strip()
                if not title:
                    continue
                results.append({"title": title, "url": href})
                seen.add(href)
            except Exception as e:
                logging.warning(f"解析搜尋結果失敗: {e}")

    driver.quit()
    logging.info(f"共找到 {len(results)} 筆 Dcard 文章")
    return results