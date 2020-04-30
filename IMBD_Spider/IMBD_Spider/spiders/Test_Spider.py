import scrapy
from IMBD_Spider.SQL_Manager import sql_manager, IMBD_movie_url_SQL
import time

class QuotesSpider(scrapy.Spider):
    name = "quotes_spider"

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
        },
        'CONCURRENT_REQUESTS': 16,
        'SPIDER_MIDDLEWARES': {
            'IMBD_Spider.middlewares.ImbdSpiderSpiderMiddleware': 543,
        },
        'DOWNLOAD_DELAY': 0,
    }

    def __init__(self):
        super(QuotesSpider, self).__init__()
        # session = sql_manager.get_sql_curser()
        # self.tid_list = session.query(IMBD_movie_url_SQL).all()
        # sql_manager.release_sql_curser(session)
        # for imd, i in enumerate(self.tid_list):
        #     tid = i.url.replace('/title/','').replace('?ref_=adv_li_tt','').replace('/','')
        #
        #     detail_url = 'https://www.imdb.com/title/%s' % tid
        #     urls.append(detail_url)

    def start_requests(self):
        urls = []
        for i in range(10):
            urls.append('http://quotes.toscrape.com/page/%d/'%(i+1))

        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse)

    def parse(self, response):
        print('suceess: ',response.url)