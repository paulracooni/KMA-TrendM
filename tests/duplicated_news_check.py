#%%
import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import sys
sys.path.append("/app")
from time import time
from datetime import datetime, timedelta

import pandas as pd
from celery import chain, group

from src.models import NewsDB, News, Image, Video, RelNewsReporter
from tasks import (
    read_keywords,
    read_topics,
    crawling_news_kr,
    crawling_news_en, )

def delete_news(news_id, today):

    news = News.select().where(
        News.id==news_id, News.date_get==today).get()
    
    if news == None:
        return None

    with NewsDB._meta.database.atomic():
        Image.delete().where(Image.news == news).execute()
        Video.delete().where(Video.news == news).execute()
        RelNewsReporter.delete().where(RelNewsReporter.news == news).execute()
        News.delete().where(News.id == news_id).execute()


st = time()
# Crawlng task

task_collect_en = group(*(crawling_news_en.s(topic) for topic in read_topics()))

task_collect_kr = group(*(crawling_news_kr.s(keyword, 20) for keyword in read_keywords()))

print("Start crawling")
res_en = task_collect_en.delay()
res_kr = task_collect_kr.delay()

params = dict(propagate=False, disable_sync_subtasks=False)
res_en.get(**params)
print("End - task_collect_en")
res_kr.get(**params)
print("End - task_collect_kr")

# Drop duplicated
today = datetime.now().strftime("%Y-%m-%d")
df = pd.DataFrame(list(News.select().where(News.date_get==today).dicts()))
for news_id in df[df.url.duplicated()].id.values:
    delete_news(news_id, today)

df = pd.DataFrame(list(News.select().where(News.date_get==today).dicts()))
for news_id in df[df.url_origin.duplicated()].id.values:
    delete_news(news_id, today)

df = pd.DataFrame(list(News.select().where(News.date_get==today).dicts()))
for news_id in df[df.title.duplicated()].id.values:
    delete_news(news_id, today)

df = pd.DataFrame(list(News.select().where(News.date_get==today).dicts()))
duplicated = df.url.duplicated().sum()
duplicated += df.url_origin.duplicated().sum()
duplicated += df.title.duplicated().sum()

print(f"Total exec time : {timedelta(seconds=time()-st)}")
print(f"Total crawled   : {len(df)}")
print(f"Total duplicated: {duplicated}")
# python ./tests/duplicated_news_check.py
