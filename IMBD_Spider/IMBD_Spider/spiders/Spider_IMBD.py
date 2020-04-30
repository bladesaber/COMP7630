import scrapy
from scrapy.spiders import CrawlSpider,Rule
from scrapy.linkextractors import LinkExtractor
from scrapy.spidermiddlewares.httperror import HttpError
from twisted.internet.error import DNSLookupError
from twisted.internet.error import TimeoutError, TCPTimedOutError
from IMBD_Spider.SQL_Manager import IMBD_spider_SQL, IMBD_movie_url_SQL, sql_manager
import time

class Imdb_spider(CrawlSpider):
    name = 'IMBD_spider'

    def generate_url(self):
        urls = []
        for i in range(20):
            url = 'https://www.imdb.com/search/title/?title_type=feature,tv_movie&num_votes=5000,&colors=color&adult=include&view=simple&count=250&start=%d&ref_=adv_nxt'\
                  %((i+1)*250+1)
            urls.append(url)
        return urls

    def start_requests(self):
        urls = [
            # 'http://quotes.toscrape.com/page/1/',
            # 'http://quotes.toscrape.com/pag/2/',
            # 'https://www.imdb.com/search/title/?title_type=feature,tv_movie&num_votes=5000,&colors=color&adult=include&view=simple&count=250',
            # 'https://www.imdb.com/search/title/?title_type=feature,tv_movie&num_votes=5000,&colors=color&adult=include&view=simple&count=250&start=251&ref_=adv_nxt',
        ]
        # urls = self.generate_url()
        urls.insert(0, 'https://www.imdb.com/search/title/?title_type=feature,tv_movie&num_votes=5000,&colors=color&adult=include&view=simple&count=250')
        for url in urls:
            yield scrapy.Request(url=url, callback=self.parse, errback=self.error_back, meta={'time':time.time()})

    allowed_domains = ['imdb.com']
    domains_name = 'https://www.imdb.com'

    custom_settings = {
        # 'ITEM_PIPELINES': {
        #     'IMBD_Spider.pipelines.ImbdSpiderPipeline': 300,
        # },
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'upgrade-insecure-requests': 1,
        },
        'CONCURRENT_REQUESTS': 16,
        'SPIDER_MIDDLEWARES': {
            'IMBD_Spider.middlewares.ImbdSpiderSpiderMiddleware': 543,
        }
    }

    def __init__(self):
        super(Imdb_spider, self).__init__()
        print('init finish')

    def __delete__(self, instance):
        super(Imdb_spider, self).__delattr__(instance)
        print('delete')

    def get_response_status(self, response):
        url = response.url
        status = response.status
        headers = response.headers
        request = response.request

        print('url: ',url)
        print('status: ',status)
        print('header: ',headers)

        return [url, status, headers, request]

    def get_request_status(self, request):
        url = request.url
        headers = request.headers
        method = request.method
        cookies = request.cookies

        print('url: ', url)
        print('method: ', method)
        print('header: ', headers)
        print('cookies: ',cookies)

        return [url, headers, method, cookies]

    def test(self):
        # html = etree.HTML(response.body)
        # self.urls.append('http://quotes.toscrape.com/author/Albert-Einstein/')

        # print('hello scrapy')
        # url = 'http://quotes.toscrape.com/author/Albert-Einstein/'
        # yield scrapy.Request(url=url, callback=self.parse)

        # link = LinkExtractor(restrict_xpaths='//div[@class="col-md-8"]/div[1]//div[@class="tags"]')
        # links = link.extract_links(response)
        # for i in links:
        #     print(i)
        pass

    index = 0
    def parse(self, response):
        receive_time = time.time()

        if response.status == 200:
            session = sql_manager.get_sql_curser()
            movie_list = response.xpath('//div[@id="wrapper"]//div[@id="main"]//div[@class="lister-item mode-simple"]')
            if len(movie_list)>0:
                movie_list_sql = []
                for movie in movie_list:
                    title = movie.xpath('.//span[@class="lister-item-header"]/span[2]/a/text()')
                    url = movie.xpath('.//span[@class="lister-item-header"]/span[2]/a/@href')
                    if len(title)>0 and len(url)>0:
                        movie_list_sql.append(IMBD_movie_url_SQL(title=title[0].extract(), url=url[0].extract()))

                session.add_all(movie_list_sql)
                session.commit()

            session.add(IMBD_spider_SQL(url=response.url, status=str(response.status)))
            session.commit()

            self.index += 1
            print('%d successfully crawl %s receive_time:%f'
                  %(self.index , response.url, receive_time-response.meta['time']))
            sql_manager.release_sql_curser(session)

            if self.index<=100:
                next_page = response.xpath('//body//a[@class="lister-page-next next-page"]')
                if next_page:
                    next_page_url = self.domains_name + next_page[0].xpath('./@href')[0].extract()
                    print('new url:%s'%next_page_url)
                    yield scrapy.Request(url=next_page_url, callback=self.parse, errback=self.error_back, meta={'time':time.time()})
                else:
                    print('no new url')
            else:
                print('too much pages')

    def error_back(self, response):
        print('fail crawl:',response.value.response.url)

        session = sql_manager.get_sql_curser()
        # 日志记录所有的异常信息
        session.add(IMBD_spider_SQL(
            url = response.value.response.url,
            status = str(response.value.response.status)
        ))
        session.commit()
        sql_manager.release_sql_curser(session)

        # self.logger.error(repr(response))
        # if response.check(HttpError):
        #     # HttpError由HttpErrorMiddleware中间件抛出
        #     # 可以接收到非200 状态码的Response
        #     response = response.value.response
        #     self.logger.error('HttpError on %s', response.url)
        #
        # elif response.check(DNSLookupError):
        #     # 此异常由请求Request抛出
        #     request = response.request
        #     self.logger.error('DNSLookupError on %s', request.url)
        #
        # elif response.check(TimeoutError, TCPTimedOutError):
        #     request = response.request
        #     self.logger.error('TimeoutError on %s', request.url)
