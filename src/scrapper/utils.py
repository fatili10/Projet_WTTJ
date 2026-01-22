from fake_useragent import UserAgent
import requests
from bs4 import BeautifulSoup

def get_user_agent():
    return UserAgent().random

def get_page_time(url_job):
    user_agent = get_user_agent()
    r = requests.get(url_job, headers={"User-Agent": user_agent})
    if r.status_code == 200:
        soup = BeautifulSoup(r.content, "html.parser")
        time_element = soup.find("time", datetime=True)
        return time_element['datetime'] if time_element else None
    return None

def fetch_data(url):
    return requests.get(url).json()
