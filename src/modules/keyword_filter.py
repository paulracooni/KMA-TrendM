import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from time import sleep, time
from itertools import chain

import numpy as np

from src.models import News, NewsDB, Embedding
from src.modules.news_gpt import ChatGPT
from src.utils.logger import DbLogger

logger = DbLogger(__name__.split(".")[-1])

def read_keywords_filter():
    path_txt = DIR_ROOT / "data/input/keywords_filter.txt"

    with path_txt.open("r", encoding='utf-8') as f:
        keywords = [
            keyword.replace("\n", "")
            for keyword in f.readlines() ]
    return keywords

class KeywordFilter:
    
    filter_keywords = read_keywords_filter()
    
    def __call__(self, news_ids):
        # Filter news_ids with keywords
        news_list = News.select().where(News.id << news_ids)
        filtered_news_id = [ news.id
            for news in news_list
            if self.need_to_filter(news) ]
        
        # Logging filtered news counts
        original_len = len(news_ids)
        filtered_len = len(filtered_news_id)
        logger.info(
            f"Filtered news {filtered_len}/{original_len}",
            not_db=True)
        
        return filtered_news_id
    
    def need_to_filter(self, news):
        for keyword in self.filter_keywords:
            if keyword in news.title or keyword in news.article:
                return True
        return False