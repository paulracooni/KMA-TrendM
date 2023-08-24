import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from tqdm import tqdm
from pprint import pprint
from src.models import News, GptResult
from src.modules.news_gpt.determinator.gpt_determinator import GptDeterminator

gpt_determintor = GptDeterminator()


# Single task
# news = News.select()[46]
# print(news.url_origin)
# print(news.title)
# result_id = gpt_determintor(news)
# result = GptResult.select().where(GptResult.id==result_id).get()
# pprint(result.data)


# Multiple task
st, et = 230, 240
result_ids = []
for news in tqdm(News.select()[st:et]):
    try:
        result_ids.append(gpt_determintor(news))
    except Exception as e:
        print(e)
        print(news.url_origin)

for id in result_ids:
    result = GptResult.select().where(GptResult.id==id).get()
    pprint(result.news.title)
    pprint(result.news.url_origin)
    pprint(result.data)