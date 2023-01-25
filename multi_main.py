import multiprocessing
import logging
import json
from os import mkdir
from os.path import exists
import re
import requests
from urllib.parse import urljoin
#%%
BASE_URL = 'https://ssr1.scrape.center'
TOTAL_PAGE = 10
logging.basicConfig(level=logging.INFO, format= '%(asctime)s - %(levelname)s : %(message)s')


#%%
# get the content of the url

def scrape_page(url):
    logging.info('scraping %s ...', url)
    try:
        r = requests.get(url)
        if r.status_code == 200:
            return r.text
        logging.error('get invalid status code %s while scraping %s', r.status_code, url)
    except requests.RequestException:
        logging.error('error occurred while scraping %s', url, exc_info=True)
#%%
# get the url of the

def parse_index(h):
    p = re.compile('<a.*?href="(.*?)".*?class="name"')
    items = re.findall(p, h)
    if not items:
        return []
    for item in items:
        detail_url = urljoin(BASE_URL, item)
        logging.info('get detailed page %s', detail_url)
        yield detail_url
#%%
# generate and get the content of the page

def scrape_index(page):
    index_url = f'{BASE_URL}/page/{page}'
    return scrape_page(index_url)
#%%
def scrape_detail(url):
    return scrape_page(url)
#%%
def parse_detail(html):
    cover_pattern = re.compile('class="item.*?<img.*?src="(.*?)".*?class="cover">', re.S)
    cover = re.search(cover_pattern, html).group(1).strip() if re.search(cover_pattern, html) else None

    name_pattern = re.compile('<h2.*?>(.*?)</h2>')
    name = re.search(name_pattern, html).group(1).strip() if re.search(name_pattern, html) else None

    return {
        "cover":cover,
        "name":name
    }

RESULT_DIR = 'results'
exists(RESULT_DIR) or mkdir(RESULT_DIR)

def save_data(data):
    name = data.get('name')
    data_path = f'{RESULT_DIR}/{name}.json'
    json.dump(data, open(data_path, 'w', encoding='utf-8'), ensure_ascii=False, indent=2)

def multi_main(page):
    html_detail = scrape_index(page)
    detail_urls = parse_index(html_detail)
    for detail_url in list(detail_urls):
        html = scrape_detail(detail_url)
        result = parse_detail(html)
        logging.info('get detail data %s', result)
        logging.info('saving data to json file')
        save_data(result)
        logging.info('saving data successfully')

