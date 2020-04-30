# -*- coding: utf-8 -*-
import scrapy
from IMBD_Spider.SQL_Manager import sql_manager, IMBD_movie_SQL, IMBD_spider_SQL, IMBD_keyword_SQL, IMBD_summary_SQL, \
    IMBD_movie_url_SQL
import time


class DetailSpider(scrapy.Spider):
    name = 'detail_Spider'

    allowed_domains = ['imdb.com']
    domains_name = 'https://www.imdb.com'

    custom_settings = {
        'DEFAULT_REQUEST_HEADERS': {
            'Accept': 'text/html,application/xhtml+xml,application/xml;q=0.9,*/*;q=0.8',
            'Accept-Language': 'en',
            'upgrade-insecure-requests': 1,
        },
        'CONCURRENT_REQUESTS': 32,
        'SPIDER_MIDDLEWARES': {
            'IMBD_Spider.middlewares.ImbdSpiderSpiderMiddleware': 543,
        },
        'DOWNLOAD_DELAY': 0,
    }

    def __init__(self):
        super(DetailSpider, self).__init__()
        self.index = 0

        session = sql_manager.get_sql_curser()
        self.tid_list = session.query(IMBD_movie_url_SQL).all()
        sql_manager.release_sql_curser(session)

        print('init finish')

    def start_requests(self):
        # urls = [
        #     'https://www.imdb.com/title/tt6751668',
        #     'https://www.imdb.com/title/tt6751668/keywords',
        #     'https://www.imdb.com/title/tt1051906/plotsummary',
        # ]
        # yield scrapy.Request(url=urls[0], callback=self.parse_detail, errback=self.error_back,meta={'tid': 'tt6751668', 'time': time.time()})
        # yield scrapy.Request(url=urls[1], callback=self.parse_keywords, errback=self.error_back, meta={'tid':'tt6751668', 'time': time.time()})
        # yield scrapy.Request(url=urls[2], callback=self.parse_summary, errback=self.error_back,
        #                      meta={'tid': 'tt1051906', 'time': time.time()})

        for imd, i in enumerate(self.tid_list):
            tid = i.url.replace('/title/','').replace('?ref_=adv_li_tt','').replace('/','')

            detail_url = 'https://www.imdb.com/title/%s' % tid
            summary_url = 'https://www.imdb.com/title/%s/plotsummary' % tid
            yield scrapy.Request(url=detail_url, callback=self.parse_detail, errback=self.error_back,
                                 meta={'tid': tid, 'time': time.time()})
            yield scrapy.Request(url=summary_url, callback=self.parse_summary, errback=self.error_back,
                                 meta={'tid': tid, 'time': time.time()})

    def parse_detail(self, response):
        receive_time = time.time()
        self.index += 1

        if response.status == 200:
            try:
                title = response.xpath('//body//div[@class="title_wrapper"]/h1/text()')
                title = title[0].extract().replace('\n', '').strip() if len(title) > 0 else None

                grading = response.xpath('//body//div[@class="title_wrapper"]/div[@class="subtext"]/text()')
                grading = grading[0].extract().replace('\n', '').strip() if len(grading) > 0 else None

                release_date = response.xpath('//span[@id="titleYear"]/a/text()')
                release_date = int(release_date[0].extract()) if len(release_date) > 0 else None

                rating = response.xpath('//div[@class="ratings_wrapper"]//span[@itemprop="ratingValue"]/text()')
                rating = float(rating[0].extract()) if len(rating) > 0 else None

                vote = response.xpath('//div[@class="ratings_wrapper"]//span[@itemprop="ratingCount"]/text()')
                vote = int(vote[0].extract().replace(',', '')) if len(vote) > 0 else None

                genres, rumtime, language, country, key_words = None, None, None, None, None
                director, writer, other_names = None, None, None
                production_company, cast = None, None
                for cell in response.xpath('//div[@id="titleDetails"]//div[@class="txt-block"]'):
                    if len(cell.xpath('./h4/text()')) > 0:
                        if cell.xpath('./h4/text()')[0].extract().replace(':', '') == 'Runtime':
                            rumtime = int(cell.xpath('./time/text()')[0].extract().replace('min', '').strip())

                        if cell.xpath('./h4/text()')[0].extract().replace(':', '') == 'Country':
                            country = '|'.join(cell.xpath('./a/text()').extract()).replace('\n', '').strip()

                        if cell.xpath('./h4/text()')[0].extract().replace(':', '') == 'Language':
                            language = '|'.join(cell.xpath('./a/text()').extract()).replace('\n', '').strip()

                        # if cell.xpath('./h4/text()')[0].extract().replace(':', '') == 'Also Known As':
                        #     other_names = ' '.join(cell.xpath('./text()').extract())
                        #     other_names = other_names.replace('\n', '').strip()

                        if cell.xpath('./h4/text()')[0].extract().replace(':', '') == 'Production Co':
                            production_company = '|'.join(cell.xpath('./a/text()').extract()).replace('\n', '').replace(
                                '| ', '|').strip()

                for cell in response.xpath('//div[@id="titleStoryLine"]//div[@class="see-more inline canwrap"]'):
                    if len(cell.xpath('./h4/text()')) > 0:
                        if 'Genre' in cell.xpath('./h4/text()')[0].extract().replace(':', ''):
                            genres = '|'.join(cell.xpath('./a/text()').extract()).replace('\n', '').strip()

                        if 'Plot Keyword' in cell.xpath('./h4/text()')[0].extract().replace(':', ''):
                            if len(cell.xpath('./nobr')) > 0:
                                key_words = None
                                # print('having more keywords')
                                keyword_url = 'https://www.imdb.com/title/%s/keywords' % response.meta['tid']
                                yield scrapy.Request(url=keyword_url, callback=self.parse_keywords,
                                                     errback=self.error_back,
                                                     meta={'tid': response.meta['tid'], 'time': time.time()})
                            else:
                                key_words = '|'.join(cell.xpath('./a/span/text()').extract()).replace('\n', '').strip()

                for cell in response.xpath('//div[@class="plot_summary "]//div[@class="credit_summary_item"]'):
                    if len(cell.xpath('./h4/text()')) > 0:
                        if 'Director' in cell.xpath('./h4/text()')[0].extract().replace(':', ''):
                            director = []
                            for a in cell.xpath('./a'):
                                dire = a.xpath('./text()')[0].extract().strip()
                                if 'more' not in dire:
                                    director.append(dire)
                            director = '|'.join(director).replace('\n', '').strip()

                        if 'Writer' in cell.xpath('./h4/text()')[0].extract().replace(':', ''):
                            writer = []
                            for a in cell.xpath('./a'):
                                writ = a.xpath('./text()')[0].extract().strip()
                                if 'more' not in writ:
                                    writer.append(writ)
                            writer = '|'.join(writer).replace('\n', '').strip()

                if len(response.xpath('//div[@id="titleCast"]//tr')) > 1:
                    cast = '|'.join(response.xpath('//div[@id="titleCast"]//tr/td[2]/a/text()').extract()).replace('\n',
                                                                                                                   '').replace(
                        '| ', '|').strip()

                session = sql_manager.get_sql_curser()
                session.add(IMBD_movie_SQL(
                    tid=response.meta['tid'],
                    title=title,
                    Grading=grading,
                    RunTime=rumtime,
                    Genres=genres,
                    Release=release_date,
                    Vote=vote,
                    Rating=rating,
                    Country=country,
                    Language=language,
                    Production=production_company,
                    Director=director,
                    Writer=writer,
                    Cast=cast
                ))
                session.commit()

                if key_words != None:
                    session.add(IMBD_keyword_SQL(
                        tid=response.meta['tid'],
                        keyword=key_words
                    ))
                    session.commit()

                session.add(IMBD_spider_SQL(
                    url=response.url, status=str(response.status), remark=response.meta['tid']
                ))
                session.commit()
                sql_manager.release_sql_curser(session)

                print('%d successfully crawl %s receive_time:%f' % (
                    self.index, response.url, receive_time - response.meta['time']))
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

    def parse_summary(self, response):
        try:
            receive_time = time.time()
            self.index += 1

            li_list = response.xpath('//ul[@id="plot-summaries-content"]//li')
            summary_list = []
            summary = []
            for li in li_list:
                if len(li.xpath('./div[@class="author-container"]')) > 0:
                    summary.append(li.xpath('.//p')[0].xpath('string(.)')[0].extract())
                    summary_text = ' '.join(summary).replace('\n', '').strip()
                    summary_list.append(summary_text)
                    summary = []
                else:
                    summary.append(li.xpath('.//p')[0].xpath('string(.)')[0].extract())

            synopsis = response.xpath('//ul[@id="plot-synopsis-content"]/li[@class="ipl-zebra-list__item"]')
            if len(synopsis) > 0:
                synopsis = synopsis[0].xpath('string(.)')[0].extract().replace('\n', '').strip()
            else:
                synopsis = None

            summary_upload_list = []
            for t in summary_list:
                if t != None:
                    summary_upload_list.append(IMBD_summary_SQL(
                        tid=response.meta['tid'],
                        summary=t,
                        type=0
                    ))

            if synopsis != None:
                summary_upload_list.append(IMBD_summary_SQL(
                    tid=response.meta['tid'],
                    summary=synopsis,
                    type=1
                ))

            session = sql_manager.get_sql_curser()
            if len(summary_upload_list) > 0:
                session.add_all(summary_upload_list)
                session.commit()

            session.add(IMBD_spider_SQL(
                url=response.url, status=str(response.status), remark=response.meta['tid']
            ))
            session.commit()
            sql_manager.release_sql_curser(session)

            print('%d successfully crawl %s receive_time:%f' % (
                self.index, response.url, receive_time - response.meta['time']))

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
            print('-------------------------------')

    def parse_keywords(self, response):
        try:
            receive_time = time.time()
            self.index += 1

            key_words = '|'.join(
                response.xpath('//div[@id="keywords_content"]/table//td/@data-item-keyword').extract()).strip()

            session = sql_manager.get_sql_curser()

            session.add(IMBD_keyword_SQL(
                tid=response.meta['tid'],
                keyword=key_words
            ))
            session.commit()

            session.add(IMBD_spider_SQL(
                url=response.url, status=str(response.status), remark=response.meta['tid']
            ))
            session.commit()
            sql_manager.release_sql_curser(session)

            print('%d successfully crawl %s receive_time:%f' % (
                self.index, response.url, receive_time - response.meta['time']))
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
            print('-------------------------------')

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
