from concurrent.futures import ThreadPoolExecutor
import datetime
import logging
import os
import sys
import requests
from bs4 import BeautifulSoup
import re

from logging.handlers import TimedRotatingFileHandler

headers = {
    'Referer': 'https://avidreaders.ru/download/master-i-margarita.html?f=epub',
    'Upgrade-Insecure-Requests': '1',
    'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 '
                  'Safari/537.36',
    'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
    'sec-ch-ua-mobile': '?0',
    'sec-ch-ua-platform': '"Windows"',
}

FORMATTER = logging.Formatter("%(asctime)s — %(name)s — %(levelname)s — %(message)s")
LOG_FILE = "logs/my_app.log"
path_to_save_book = 'all_books1'


def get_console_handler():
    console_handler = logging.StreamHandler(sys.stdout)
    console_handler.setFormatter(FORMATTER)
    return console_handler


def get_file_handler():
    file_handler = TimedRotatingFileHandler(LOG_FILE, when='midnight')
    file_handler.setFormatter(FORMATTER)
    return file_handler


def get_logger(logger_name):
    logger = logging.getLogger(logger_name)
    logger.setLevel(logging.DEBUG)
    logger.addHandler(get_console_handler())
    logger.addHandler(get_file_handler())
    logger.propagate = False
    return logger


def download_books(url_download):
    headers = {
        'Referer': 'https://avidreaders.ru/download/master-i-margarita.html?f=epub',
        'Upgrade-Insecure-Requests': '1',
        'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, like Gecko) Chrome/126.0.0.0 Safari/537.36',
        'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
        'sec-ch-ua-mobile': '?0',
        'sec-ch-ua-platform': '"Windows"',
    }
    req_download = requests.get(url_download, headers=headers)
    if req_download.status_code == 200:
        src_download = req_download.text
        soup_download = BeautifulSoup(src_download, 'lxml')
        try:
            final_download_url = soup_download.find('div', class_='dnld-info').find('a').get('href')
            name_book_soup = (soup_download.find('div', class_='book_info download')
                              .find('h1', class_='title_lvl1').find('span')).text
            name_author_soup = soup_download.find('div', class_='author_info').find('a').text
            regex = '(?<=“).+(?<=”)'
            name_book = re.search(regex, name_book_soup).group(0)
        except AttributeError as e:
            my_logger.debug(f'{e}')
            final_download_url = None
            name_book = None
            name_author_soup = None

        if final_download_url is not None:
            headers = {
                'Referer': f'{url_download}',
                'Upgrade-Insecure-Requests': '1',
                'User-Agent': 'Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 (KHTML, '
                              'like Gecko) Chrome/126.0.0.0 Safari/537.36',
                'sec-ch-ua': '"Not/A)Brand";v="8", "Chromium";v="126", "Google Chrome";v="126"',
                'sec-ch-ua-mobile': '?0',
                'sec-ch-ua-platform': '"Windows"',
            }
            req_download_book = requests.get(final_download_url, headers=headers)
            if req_download_book.status_code == 404:
                print(final_download_url)
                print("404")
            regex = '(?<=&f=).+'
            file_extension = re.search(regex, final_download_url).group(0)
        else:
            req_download_book = None
            file_extension = None

        try:
            if name_book is None or name_author_soup is None or req_download_book is None:
                print("Somethings is NoneType")
            else:
                path, dirs, files = next(os.walk(f'./{path_to_save_book}'))
                file_count = len(files)
                my_logger.debug(f'{file_count} books download')
                with open(f"{path_to_save_book}/{name_book + name_author_soup}.{file_extension}", "wb") as f:
                    f.write(req_download_book.content)
        except OSError as e:
            my_logger.debug(f'{e}')


my_logger = get_logger("parser")

time_now = datetime.datetime.now()

URL = 'https://avidreaders.ru/books/'
for i in range(100000):
    req_main = requests.get(URL + str(i), headers=headers)
    if req_main.status_code == 200:
        print('get all books on page')
        src = req_main.text
        soup_all_books = BeautifulSoup(src, "lxml")
        books = soup_all_books.find_all('div', class_='book_name')
        links_book_list = []
        download_url_list = []

        for book in books:
            url = book.find('a').get("href")
            links_book_list.append(url)

        print(f'added books to list from page {books}')


        def create_urls_list(link_pages):
            req_book = requests.get(link_pages, headers=headers)
            if req_book.status_code == 200:
                src_book = req_book.text
                soup_book = BeautifulSoup(src_book, 'lxml')
                try:
                    download_url = soup_book.find('div', class_='format_download').find('a').get('href')
                    print(download_url)
                    download_url_list.append(download_url)
                except AttributeError:
                    pass


        with ThreadPoolExecutor(max_workers=None) as executor:
            results = list(executor.map(create_urls_list, links_book_list))

        print(f'create list downloads for books {download_url_list}')

        with ThreadPoolExecutor(max_workers=None) as executor:
            executor.map(download_books, download_url_list)
