import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from pprint import pprint
from src.models import News, GptResult
from src.modules.news_gpt.classifier.gpt_cls_sector import GptClsSector
from src.modules.news_gpt.summarizer.gpt_summary import GptSummary

gpt_summary = GptSummary()
gpt_cls1 = GptClsSector()

news = News.select()[99]


print(news.url_origin)
result_id = gpt_summary(news)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)


result_id = gpt_cls1(result_id)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)