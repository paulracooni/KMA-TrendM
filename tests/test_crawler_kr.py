#%%
import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import pandas as pd
from tasks import read_keywords
from modules.news_crawlers import NaverNewsCrawler

list_news = []
crawler = NaverNewsCrawler()
for keyword in read_keywords():
    news_objs = crawler.crawling(keyword)
    list_news.extend([news_obj.get("news") for news_obj in news_objs ])

news = pd.DataFrame(crawler)
#%%