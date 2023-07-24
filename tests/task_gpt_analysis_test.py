import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from tqdm import tqdm
from tasks import gpt_analysis, publish_trend_m
from models import News, GptResult
from modules.news_gpt import Determinator


st = 20
et = 30



results = []
for news in tqdm(News.select()[st:et]):
    results.append(gpt_analysis(news_id=news.id))


publish_trend_m(ids = results)