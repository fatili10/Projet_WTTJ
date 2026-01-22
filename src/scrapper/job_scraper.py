# from selenium import webdriver
# from selenium.webdriver.common.by import By
# from selenium.webdriver.chrome.options import Options
# from datetime import datetime
# import pandas as pd
# from .utils import get_page_time

# def head_info():
#     chrome_options = Options()
#     chrome_options.add_argument("--headless")
#     chrome_options.add_argument('--no-sandbox')
#     chrome_options.add_argument('--disable-dev-shm-usage')
#     return chrome_options

# def get_all_data(keyword, country, country_code):
#     driver = webdriver.Chrome(options=head_info())
#     p = 1
#     results = []

#     while True:
#         url = f'https://www.welcometothejungle.com/en/jobs?refinementList%5Boffices.country_code%5D%5B%5D={country_code}&query={keyword}&page={p}&aroundQuery={country}&searchTitle=True'
#         driver.get(url)
#         driver.implicitly_wait(10)

#         jobs = driver.find_elements(By.CSS_SELECTOR, '[data-testid="search-results-list-item-wrapper"]')
#         if not jobs:
#             break

#         for job in jobs:
#             try:
#                 link = job.find_element(By.CSS_SELECTOR, 'a[href^="/en/companies"]').get_attribute('href')
#                 date_annonce = get_page_time(link)
#                 results.append({
#                     "link": link,
#                     "date_annonce": date_annonce,
#                     "date_extract": datetime.today().strftime("%Y-%m-%dT%H:%M:%SZ")
#                 })
#             except Exception as e:
#                 print(f"Erreur sur une annonce : {e}")

#         p += 1

#     driver.quit()
#     return pd.DataFrame(results)
from selenium import webdriver
from selenium.webdriver.common.by import By
from selenium.webdriver.chrome.options import Options
from datetime import datetime
from fake_useragent import UserAgent
import pandas as pd
import requests
from bs4 import BeautifulSoup

def _chrome_options():
    options = Options()
    options.add_argument("--headless")
    options.add_argument("--no-sandbox")
    options.add_argument("--incognito")
    options.add_argument(f"user-agent={UserAgent().random}")
    return options

def _get_publish_date(url):
    r = requests.get(url, headers={"User-Agent": UserAgent().random})
    if r.status_code != 200:
        return None
    soup = BeautifulSoup(r.content, "html.parser")
    time_tag = soup.find("time", datetime=True)
    return time_tag["datetime"] if time_tag else None

def get_all_data(keyword, country, country_code):
    driver = webdriver.Chrome(options=_chrome_options())
    page = 1
    rows = []

    while True:
        url = (
            "https://www.welcometothejungle.com/en/jobs"
            f"?refinementList%5Boffices.country_code%5D%5B%5D={country_code}"
            f"&query={keyword}&page={page}&aroundQuery={country}&searchTitle=True"
        )

        driver.get(url)
        driver.implicitly_wait(10)

        jobs = driver.find_elements(By.CSS_SELECTOR, '[data-testid="search-results-list-item-wrapper"]')
        if not jobs:
            break

        for job in jobs:
            try:
                link = job.find_element(By.CSS_SELECTOR, 'a[href^="/en/companies"]').get_attribute("href")
                rows.append({
                    "link": link,
                    "date_annonce": _get_publish_date(link),
                    "date_extract": datetime.utcnow().isoformat()
                })
            except Exception:
                pass

        page += 1

    driver.quit()
    return pd.DataFrame(rows)

