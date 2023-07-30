import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from tqdm import tqdm
from pprint import pprint
from models import News, GptResult
from modules.news_gpt.summarizer.gpt_summary import GptSummary


# The summary characters must be between 600 to 800.

summary = GptSummary()


# Single task
# pprint(summary.sys_prompt_full)
# news = News.select()[1300]

# print(news.url_origin)
# print(news.article)
# result_id = summary(news)

# result = GptResult.select().where(GptResult.id==result_id).get()
# pprint(result.data)
# print(len(result.data['summary']))

# Multiple task
st, et = 110, 120

result_ids = [summary(news) for news in tqdm(News.select()[st:et])]

for id in result_ids:
    result = GptResult.select().where(GptResult.id==id).get()
    pprint(result.data)


for id in result_ids:
    result = GptResult.select().where(GptResult.id==id).get()
    print(len(result.data['summary']))
