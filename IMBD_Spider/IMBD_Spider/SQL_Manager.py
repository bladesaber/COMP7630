import sqlite3
import sqlalchemy
from sqlalchemy import create_engine
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.orm import sessionmaker
import queue
# conn = sqlite3.connect('D:/hongkong record/daily course/second seminster/COMP7630/Project/data.db')

sql_path = 'D:/hongkong record/daily course/second seminster/COMP7630/Project/data.db'

from sqlalchemy import Column, Integer, String, Float

Base = declarative_base()

class IMBD_spider_SQL(Base):
    # 指定本类映射到users表
    __tablename__ = 'IMBD_templte_spider'

    id = Column(Integer, primary_key=True)
    url = Column(String)
    status = Column(String)
    remark = Column(String)

    def __repr__(self):
        return "<IMBD_spider_SQL(url='%s', status_code='%s')>" % (self.url, self.status_code)

class IMBD_movie_url_SQL(Base):
    __tablename__ = 'Movie_templte_url'

    id = Column(Integer, primary_key=True)
    title = Column(String)
    url = Column(String)

    def __repr__(self):
        return "<Movie_url(title='%s', url='%s')>" % (self.title, self.url)

class IMBD_movie_SQL(Base):
    __tablename__ = 'Movie'

    id = Column(Integer, primary_key=True)
    tid = Column(String)

    title = Column(String)
    Grading = Column(String)
    RunTime = Column(String)
    Genres = Column(String)
    Release = Column(Integer)
    Vote = Column(Integer)
    Rating = Column(Float)
    Country = Column(String)
    Language = Column(String)
    Production = Column(String)
    Director = Column(String)
    Writer = Column(String)
    Cast = Column(String)

    def __repr__(self):
        return "<Movie(tid='%s', title='%s')>" % (self.tid, self.title)

class IMBD_keyword_SQL(Base):
    __tablename__ = 'Keyword'

    id = Column(Integer, primary_key=True)
    tid = Column(String)
    keyword = Column(String)

    def __repr__(self):
        return "<Keyword(tid='%s', keyword='%s')>" % (self.tid, self.keyword)

class IMBD_summary_SQL(Base):
    '''
    type: summary:0, synopsis:1
    '''
    __tablename__ = 'Summary'

    id = Column(Integer, primary_key=True)
    tid = Column(String)
    summary = Column(String)
    type = Column(Integer)

    def __repr__(self):
        return "<Summary(tid='%s', text='%s')>" % (self.tid, self.summary)

class IMBD_userRating_SQL(Base):
    __tablename__ = 'UserRating'

    id = Column(Integer, primary_key=True)
    tid = Column(String)
    userName = Column(String)
    rating = Column(Float)

    def __repr__(self):
        return "<UserRating(tid='%s', userName='%s', rating=%f)>" % (self.tid, self.summary, self.rating)

class IMBD_user_SQL(Base):
    __tablename__ = 'User'

    id = Column(Integer, primary_key=True)
    userName = Column(String)

    def __repr__(self):
        return "<User(user='%s', userLink='%s')>" % (self.id, self.userName)

class Manager_SQL(object):
    def __init__(self, sql_path):
        self.engine = create_engine(
            'sqlite:///'+sql_path,
            echo=False)

        Base.metadata.create_all(self.engine, checkfirst=True)

        Session = sessionmaker(bind=self.engine)
        self.q = queue.Queue(maxsize=1)
        # sqlite 不支持并发执行写
        self.q.put(Session())

    def get_sql_curser(self):
        return self.q.get(block=True, timeout=None)

    def release_sql_curser(self, session):
        self.q.put(session)

sql_manager = Manager_SQL(sql_path)
