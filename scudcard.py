import requests
from bs4 import BeautifulSoup
import urllib.parse
import time

def google_search_dcard(department, max_retries=3):
    """
    使用 DuckDuckGo 搜尋 '東吳 {department} 老師 site:dcard.tw'，回傳前三筆結果
    每筆結果包含 title, url, description (簡短摘要)
    """

    query = f"東吳 {department} 老師 site:dcard.tw"
    query_enc = urllib.parse.quote(query)
    url = f"https://html.duckduckgo.com/html/?q={query_enc}"

    headers = {
        "User-Agent": "Mozilla/5.0"
    }

    for attempt in range(max_retries):
        try:
            res = requests.get(url, headers=headers, timeout=10)
            res.raise_for_status()
            soup = BeautifulSoup(res.text, "html.parser")

            results = []
            for result in soup.select('.result')[:3]:
                title_tag = result.select_one('.result__a')
                desc_tag = result.select_one('.result__snippet')

                title = title_tag.text.strip() if title_tag else "無標題"
                url = title_tag['href'] if title_tag and 'href' in title_tag.attrs else ""
                description = desc_tag.text.strip() if desc_tag else "無摘要"

                results.append({
                    "title": title,
                    "url": url,
                    "description": description
                })

            # 若有結果就回傳
            if results:
                return results
        except Exception as e:
            print(f"搜尋失敗，第{attempt+1}次，錯誤訊息：{e}")
            time.sleep(1)  # 等待再重試

    # 全部失敗或沒結果
    return []