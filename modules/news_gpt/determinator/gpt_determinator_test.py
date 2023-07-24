import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from pprint import pprint
from models import News, GptResult
from modules.news_gpt.determinator.gpt_determinator import GptDeterminator

gpt_determintor = GptDeterminator()

news = News.select()[32]


print(news.url_origin)
result_id = gpt_determintor(news)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)
