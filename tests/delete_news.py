import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)
import sys; sys.path.append("/app")

from tqdm import tqdm
from datetime import datetime 
from src.models import NewsDB, News, Image, Video, RelNewsKeyword, RelNewsReporter, GptResult, TrendMArticle

def delete_news(news):

    with NewsDB._meta.database.atomic():
        Image.delete().where(Image.news == news).execute()
        Video.delete().where(Video.news == news).execute()
        RelNewsReporter.delete().where(RelNewsReporter.news == news).execute()
        RelNewsKeyword.delete().where(RelNewsKeyword.news == news).execute()
        GptResult.delete().where(GptResult.news == news).execute()
        News.delete().where(News.id == news.id).execute()
    return news.id


list_news = []
# for news in tqdm(list(News.select().where(News.date_get != datetime.strptime("2023-08-31", '%Y-%m-%d')))):
for news in tqdm(list(News.select())):
    if not TrendMArticle.select().where(TrendMArticle.news==news).exists():
        list_news.append(news)

for news in tqdm(list_news):
    delete_news(news)
