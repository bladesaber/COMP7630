from scrapy import cmdline

# cmdline.execute('scrapy crawl IMBD_spider'.split())
# cmdline.execute('scrapy crawl detail_Spider -s JOBDIR=somespider/01'.split())
# cmdline.execute('scrapy crawl detail_Spider'.split())
# cmdline.execute('scrapy crawl quotes_spider'.split())
cmdline.execute('scrapy crawl userRatings_spider -s JOBDIR=somespider/02'.split())
# cmdline.execute('scrapy crawl userRatings_spider'.split())
# cmdline.execute('quit()')

# from IMBD_Spider.SQL_Manager import sql_manager, IMBD_movie_url_SQL
# from scrapy.crawler import CrawlerProcess
# from IMBD_Spider.spiders.userRating import UserratingSpider
# import math
#
# session = sql_manager.get_sql_curser()
# tid_list = session.query(IMBD_movie_url_SQL).all()
# sql_manager.release_sql_curser(session)
#
# split_part = 6
# split_counts = math.ceil(len(tid_list)/split_part)
# start_idx = 0
#
# process = CrawlerProcess()
# for i in range(split_part):
#     end_idx = start_idx + split_counts
#     if end_idx>len(tid_list):
#         end_idx = len(tid_list)
#     process.crawl(UserratingSpider, start_idx=start_idx, end_idx=end_idx)
#     start_idx = end_idx
#
# process.start()
