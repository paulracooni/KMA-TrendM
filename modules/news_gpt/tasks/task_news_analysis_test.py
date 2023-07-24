import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from pprint import pprint
from models import News, TrendMArticle
from modules.news_gpt.tasks.task_news_analysis import TaskNewsAnalysis

news = News.select()[139]


analysis = TaskNewsAnalysis()

article_id = analysis(news.id)
if article_id != None:
    article = TrendMArticle.get_by_id(article_id)

    pprint(article.data)
else:

    pprint(f"not suitable\n{news.title}\n", )

