import logging
import collections

import bs4
import requests
import re
import csv

logging.basicConfig(level=logging.DEBUG)
logger = logging.getLogger(('wb'))

ParseResult = collections.namedtuple(
    'ParseResult',
    (
        'brand_name',
        'goods_name',
        'url',
    ),
)
HEADERS = (
    'Бренд',
    'Товар',
    'Ссылка'
)


class Client:

    def __init__(self):
        self.session = requests.Session()
        self.session.headers = {
            'User-Agent': 'Mozilla/5.0 (Macintosh; Intel Mac OS X 10_15_7) AppleWebKit/605.1.15 (KHTML, like Gecko) Version/16.3 Safari/605.1.15',
            'Accept-Language': 'ru',
        }
        self.result = []

    def load_page(self,url:str, page: int = None):
        res = self.session.get(url=url)
        res.encoding = 'UTF-8'
        return res.text

    def parse_page(self, text: str):
        soup = bs4.BeautifulSoup(text, 'lxml')
        container = soup.select('div.product-snippet_ProductSnippet__content__52z59')
        for block in container:
            self.parse_block(block=block)

    def parse_block(self, block):
        #  Достаю ссылку
        url_block = block.select_one('a')
        if not url_block:
            logger.error('no url_block')
            return
        
        url = "https://aliexpress.ru" + url_block.get('href')
        if not url:
            logger.error('no href')
        
        brand_name = block.select_one('div.product-snippet_ProductSnippet__caption__52z59').text # достаю имя бренда
        goods_name = block.select_one('div.product-snippet_ProductSnippet__name__52z59').text # достаю имя товара

        self.result.append(ParseResult(
            url=url,
            brand_name=brand_name,
            goods_name=goods_name,
        ))

    def save_csv(self, text:str):

        soup = bs4.BeautifulSoup(text, 'lxml')
        head = soup.select_one('h1').text

        with open(f"result_{head}.csv", 'w', encoding='utf-8') as file:
            writer = csv.writer(file, quoting= csv.QUOTE_MINIMAL,delimiter = ';')
            writer.writerow(HEADERS)
            for item in self.result:
                writer.writerow(item)

    def run(self, url:str):
        text = self.load_page(url=url)
        self.parse_page(text = text)
        self.save_csv(text=text)

if __name__ == '__main__':
    parser = Client()

    url = 'https://aliexpress.ru/category/202000006/computer-office.html?spm=a2g2w.home.category.4.75dfa63diXEdoU'
    
    parser.run(url=url)