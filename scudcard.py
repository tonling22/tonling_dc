def google_search_dcard(query):
    import platform
    import os
    import time
    import logging
    from selenium.webdriver.common.by import By
    from selenium.webdriver.support.ui import WebDriverWait
    from selenium.webdriver.support import expected_conditions as EC
    from selenium.webdriver.chrome.service import Service
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

    results = []
    seen = set()

    search_results = driver.find_elements(By.CSS_SELECTOR, 'div.g')
    for result in search_results:
        try:
            link_elem = result.find_element(By.CSS_SELECTOR, 'a')
            href = link_elem.get_attribute('href')

            if not href or "dcard.tw" not in href or href in seen:
                continue

            title_elem = result.find_element(By.CSS_SELECTOR, 'h3')
            title = title_elem.text.strip() if title_elem else "無標題"

            try:
                desc_elem = result.find_element(By.CSS_SELECTOR, 'div.VwiC3b')  # Google 摘要內容 class
                description = desc_elem.text.strip()
            except:
                description = "無摘要"

            results.append({
                "title": title,
                "url": href,
                "description": description
            })
            seen.add(href)
        except Exception as e:
            logging.warning(f"解析搜尋結果失敗: {e}")

    driver.quit()
    logging.info(f"共找到 {len(results)} 筆 Dcard 文章")
    return results