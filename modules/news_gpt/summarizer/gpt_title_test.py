import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from pprint import pprint
from models import News, GptResult
from modules.news_gpt.summarizer.gpt_summary import GptSummary
from modules.news_gpt.summarizer.gpt_title import GptTitle

gpt_summary = GptSummary()
gpt_title = GptTitle()
pprint(gpt_summary.sys_prompt_full)
news = News.select()[15]
print(news.url_origin)
result_id = gpt_summary(news)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)


pprint(gpt_title.sys_prompt)
result_id = gpt_title(result_id)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)

