from time import sleep, time
from datetime import datetime

import pandas as pd

from utils.logger import DbLogger
from models import NewsDB, News, Image, Video, RelNewsReporter

logger = DbLogger(__name__.split(".")[-1])

class DupRemover:

    def __init__(self, today=None):
        self.today = today \
            if today!=None \
                else datetime.now().strftime("%Y-%m-%d")


    def __call__(self, ):
        
        st = time()
        deleted = 0
        df = self.get_news()
        deleted_id = []
        for news_id in df[df.url.duplicated()].id.values:
            if self.delete_news(news_id) != None:
                deleted_id.append(news_id)
                deleted +=1

        df = self.get_news()
        for news_id in df[df.url_origin.duplicated()].id.values:
            if self.delete_news(news_id) != None:
                deleted_id.append(news_id)
                deleted +=1

        df = self.get_news()
        for news_id in df[df.title.duplicated()].id.values:
            if self.delete_news(news_id) != None:
                deleted_id.append(news_id)
                deleted +=1

        df = self.get_news()
        crawled = len(df)
        duplicated = df.url.duplicated().sum()
        duplicated += df.url_origin.duplicated().sum()
        duplicated += df.title.duplicated().sum()

        logger.info(
            f"Duplicated news deleted: {deleted=}, {duplicated=}, {crawled=}",
            data=dict(
                deleted    = int(deleted),
                duplicated = int(duplicated),
                crawled    = int(crawled),
                exec_time  = time()-st,  ))

        return list(map(int, deleted_id))

    def delete_news(self, news_id):

        news = News.select().where(
            News.id==news_id, News.date_get==self.today).get()
        
        if news == None:
            return None

        with NewsDB._meta.database.atomic():
            Image.delete().where(Image.news == news).execute()
            Video.delete().where(Video.news == news).execute()
            RelNewsReporter.delete().where(RelNewsReporter.news == news).execute()
            News.delete().where(News.id == news_id).execute()
        return news_id

    def get_news(self,):
        return pd.DataFrame(list(News.select().where(News.date_get==self.today).dicts()))