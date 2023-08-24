import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import json
import pandas as pd
from tqdm import tqdm

from src.models import News, GptResult
from src.modules.news_gpt import Determinator

path_json = DIR_ROOT / "data" / "determinator_valid.json"
news_ids = json.load(path_json.open("r"))


determinator = Determinator()
results = list()

for news_id in tqdm(news_ids):

    res_id = determinator(news_id=news_id)
    news = News.select().where(News.id==news_id).get()
    result = GptResult.select().where(GptResult.id==res_id).get()

    results.append(dict(
        news_id  = news_id,
        title    = news.title,
        usage    = result.usage,
        suitable = result.data['suitable'],
        reason   = result.data['reason'],
        link     = news.url_origin
    ))

pd.DataFrame(results).to_csv(DIR_ROOT / "determine_test.csv", index=False)