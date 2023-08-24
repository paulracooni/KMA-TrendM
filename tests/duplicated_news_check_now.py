#%%
import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import sys
sys.path.append("/app")
from time import time
from datetime import timedelta
import pandas as pd
from celery import chain, group

from src.models import News
from tasks import (
    read_keywords,
    read_topics,
    crawling_news_kr,
    crawling_news_en, )


df = pd.DataFrame(list(News.select().dicts()))

print(f"Total crawled   : {len(df)}")
print(f"Total duplicated: {df.url.duplicated().sum()}")
# python ./tests/duplicated_news_check.py