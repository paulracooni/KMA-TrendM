import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from pprint import pprint
from models import News, GptResult
from modules.news_gpt.summarizer.gpt_summary import GptSummary

summary = GptSummary()

pprint(summary.sys_prompt_full)
news = News.select()[15]


print(news.url_origin)
result_id = summary(news)


result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)
print(len(result.data['summary']))