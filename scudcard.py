def dcard_search_selenium(query):
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

    url = f"https://www.dcard.tw/search?query={query}"
    logging.info(f"前往 Dcard 搜尋頁: {url}")
    driver.get(url)

    try:
        WebDriverWait(driver, 15).until(
            EC.presence_of_element_located((By.CSS_SELECTOR, 'a[href*="/p/"]'))
        )
    except Exception as e:
        logging.warning(f"等待文章載入超時: {e}")
        driver.quit()
        return []

    SCROLL_PAUSE_TIME = 2
    MAX_SCROLLS = 8
    last_height = driver.execute_script("return document.body.scrollHeight")

    for _ in range(MAX_SCROLLS):
        driver.execute_script("window.scrollTo(0, document.body.scrollHeight);")
        time.sleep(SCROLL_PAUSE_TIME)
        new_height = driver.execute_script("return document.body.scrollHeight")
        if new_height == last_height:
            break
        last_height = new_height

    # 僅選取文章連結
    links = driver.find_elements(By.CSS_SELECTOR, 'a[href*="/p/"]')
    results = []
    seen = set()

    for link in links:
        href = link.get_attribute('href')
        if href and href not in seen:
            try:
                # 取得文章標題 (Dcard 網站使用 span 或 h2，可根據情況調整)
                title = link.text.strip()
                if not title:
                    title = link.get_attribute("title") or "無標題"
                results.append({"title": title, "url": href})
                seen.add(href)
            except Exception as e:
                logging.warning(f"解析文章失敗: {e}")

    driver.quit()
    logging.info(f"共找到 {len(results)} 筆文章")
    return results