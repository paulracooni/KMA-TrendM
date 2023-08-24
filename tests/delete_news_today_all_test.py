import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from tqdm import tqdm
from datetime import datetime 
from src.models import NewsDB, News, Image, Video, RelNewsKeyword, RelNewsReporter, GptResult

def delete_news(news):

    with NewsDB._meta.database.atomic():
        Image.delete().where(Image.news == news).execute()
        Video.delete().where(Video.news == news).execute()
        RelNewsReporter.delete().where(RelNewsReporter.news == news).execute()
        RelNewsKeyword.delete().where(RelNewsKeyword.news == news).execute()
        GptResult.delete().where(GptResult.news == news).execute()
        News.delete().where(News.id == news.id).execute()
    return news.id

news_todays = News.select().where(News.date_get == datetime.strptime("2023-08-02", '%Y-%m-%d'))
print(len(news_todays))

for news in tqdm(news_todays):
    delete_news(news)
