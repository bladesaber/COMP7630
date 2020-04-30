# -*- coding: utf-8 -*-
import scrapy
from IMBD_Spider.SQL_Manager import sql_manager, IMBD_spider_SQL, IMBD_userRating_SQL, IMBD_user_SQL, IMBD_movie_url_SQL

class UserratingSpider(scrapy.Spider):
    name = 'userRatings_spider'
    allowed_domains = ['www.imdb.com']

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'upgrade-insecure-requests': 1,
        },
        'CONCURRENT_REQUESTS': 48,
        'SPIDER_MIDDLEWARES': {
            'IMBD_Spider.middlewares.ImbdSpiderSpiderMiddleware': 543,
        },
        'DOWNLOAD_DELAY': 0,
        'DEPTH_LIMIT':10,
        'LOG_LEVEL': "WARNING",
    }

    def __init__(self, start_idx=0, end_idx=0):
        super(UserratingSpider, self).__init__()
        self.index = 0
        # self.start_idx = start_idx
        # self.end_idx = end_idx

        session = sql_manager.get_sql_curser()
        self.tid_list = session.query(IMBD_movie_url_SQL).all()
        sql_manager.release_sql_curser(session)
        self.tid_list = self.tid_list[5000:10000]

        print('init finish')

    def start_requests(self):
        # tt6751668
        # urls = [
        #     'https://www.imdb.com/title/tt6751668/reviews'
        # ]
        # yield scrapy.Request(url=urls[0], callback=self.parse, errback=self.error_back, meta={'tid':'tt6751668'})

        for i in self.tid_list:
            tid = i.url.replace('/title/','').replace('?ref_=adv_li_tt','').replace('/','')
            url = 'https://www.imdb.com/title/%s/reviews'%tid
            yield scrapy.Request(url=url, callback=self.parse, errback=self.error_back, meta={'tid': tid})

    def get_next_url(self, response, tid):
        data_key = response.xpath('//div[@class="load-more-data"]/@data-key')
        if len(data_key)>0:
            data_key = '&ref_=undefined&paginationKey=' + data_key[0].extract()
            origin = 'http://www.imdb.com/title/%s/reviews/_ajax?sort=helpfulnessScore&dir=desc&spoiler=hide&ratingFilter=0' % tid
            return origin + data_key
        else:
            return ''

    def get_review_list(self, response, tid):
        review_list = response.xpath('//div[@class="lister-list"]/div[@class="lister-item mode-detail imdb-user-review  collapsable"]')
        result_list = []
        user_list = []

        for review in review_list:
            score = review.xpath('.//span[@class="rating-other-user-rating"]/span[1]/text()')
            item = IMBD_userRating_SQL()
            user_item = IMBD_user_SQL()
            item.tid = tid

            if len(score)>0:
                score = score[0].extract()
                item.rating = float(score)

            user = review.xpath('.//div[@class="display-name-date"]//a/text()')
            if len(user)>0:
                user = user[0].extract()
                item.userName = user
                user_item.userName = user

            user_link = review.xpath('.//div[@class="display-name-date"]//a/@href')
            if len(user_link)>0:
                user_link = user_link[0].extract()
                try:
                    user_id = int(user_link.replace('/?ref_=tt_urv','').replace('/user/ur','').replace('/',''))
                    user_item.id = user_id
                    user_list.append(user_item)
                except:
                    pass

            result_list.append(item)
        return result_list, user_list

    def parse(self, response):
        self.index += 1

        if response.status == 200:
            try:
                tid = response.meta['tid']
                item_list, user_list = self.get_review_list(response, tid)

                session = sql_manager.get_sql_curser()
                if len(item_list)>0:
                    session.add_all(item_list)
                    # session.commit()

                # if len(user_list):
                #     for item in user_list:
                #         session.merge(item)
                #     session.commit()

                session.add(IMBD_spider_SQL(
                    url=response.url, status=str(response.status), remark=tid
                ))
                session.commit()
                sql_manager.release_sql_curser(session)

                next_url = self.get_next_url(response, tid=tid)
                if next_url != '':
                    yield scrapy.Request(url=next_url, callback=self.parse, errback=self.error_back, meta={'tid': tid})

                print('%d successfully crawl %s' % (self.index, response.url))

            except Exception as e:
                session = sql_manager.get_sql_curser()
                session.add(IMBD_spider_SQL(
                    url=response.url,
                    status=str(999),
                    remark=response.meta['tid']
                ))
                session.commit()
                sql_manager.release_sql_curser(session)
                print(e)
                print('error happen %s' % response.url)

    def error_back(self, response):
        print('fail crawl:', response.value.response.url)

        session = sql_manager.get_sql_curser()
        session.add(IMBD_spider_SQL(
            url=response.value.response.url,
            status=str(response.value.response.status),
            remark=response.meta['tid']
        ))
        session.commit()
        sql_manager.release_sql_curser(session)