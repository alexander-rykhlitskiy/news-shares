import os
from bs4 import BeautifulSoup as bs
import requests
import json
from datetime import date, timedelta
from url_to_path import url_to_path
from multiprocessing import Process

DAY_URL_PATTERN = 'https://news.tut.by/archive/{}.html'

def parse_html(html):
    return bs(html, 'lxml')

def fetch_page(url):
    print(url)
    return parse_html(requests.get(url).text)

def page_doc(url, prefix=None):
    dir_path = f"tmp/{prefix or ''}"
    file_path = os.path.join(dir_path, url_to_path(url))
    os.makedirs(os.path.dirname(file_path), exist_ok=True)

    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return parse_html(f.read())
    else:
        result = fetch_page(url)
        with open(file_path, 'w') as f:
            f.write(str(result))
        return result

def fetch_page_stats(date, url):
    doc = page_doc(url, prefix=date)
    data = doc.find('div', {'data-banner': True, 'data-content': True})

    if data:
        result = dict([soc_net.split(':') for soc_net in data['data-content'].split(',')])
        ul = doc.find('ul', {'class': 'b-article-info-tags'})
        if ul:
            result['tags'] = [a.text for a in ul.findAll('a')]
        else:
            print(f"NO TAGS FOR {url}")
        result['title'] = doc.find('h1').text
        return result
    else:
        print(f"NO DATA FOR {url}")
        return None

def fetch_day_stats(date):
    url = DAY_URL_PATTERN.format(date)
    links = [entry['href'] for entry in page_doc(url).select('.b-news .news-entry a.entry__link')]

    result = {}
    for link in links:
        result[link] = fetch_page_stats(date, link)

    return result

def get_stats(date):
    file_path = f'tmp/{date}.json'
    if os.path.exists(file_path):
        with open(file_path, 'r') as f:
            return json.load(f)
    else:
        stats = fetch_day_stats(date)
        with open(file_path, 'w', encoding='utf8') as f:
            f.write(json.dumps(stats, indent=4, ensure_ascii=False))

os.makedirs('tmp', exist_ok=True)

start_date = date(2020, 1, 1)
end_date = date.today()
delta = timedelta(days=1)

date = start_date
while date <= end_date:
    print (date)
    print(get_stats(date.strftime("%d.%m.%Y")))
    date += delta
