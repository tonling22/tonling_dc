import requests
from bs4 import BeautifulSoup
import urllib.parse

def google_search_dcard(department):
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

    res = requests.get(url, headers=headers)
    res.raise_for_status()
    soup = BeautifulSoup(res.text, "html.parser")

    results = []
    for result in soup.select('.result')[:3]:
        title_tag = result.select_one('.result__a')
        desc_tag = result.select_one('.result__snippet')

        title = title_tag.text if title_tag else "無標題"
        url = title_tag['href'] if title_tag and 'href' in title_tag.attrs else ""
        description = desc_tag.text if desc_tag else "無摘要"

        results.append({
            "title": title,
            "url": url,
            "description": description
        })

    return results