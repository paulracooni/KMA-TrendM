import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from pprint import pprint
from models import News, GptResult
from modules.news_gpt.summarizer.gpt_summary import GptSummary
from modules.news_gpt.summarizer.gpt_keywords import GptKeywords

gpt_summary = GptSummary()
gpt_keywords = GptKeywords()
pprint(gpt_summary.sys_prompt_full)
news = News.select()[28]
print(news.url_origin)
result_id = gpt_summary(news)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)


pprint(gpt_keywords.sys_prompt)
result_id = gpt_keywords(result_id)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)

