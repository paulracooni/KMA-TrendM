import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)
import sys; sys.path.append(DIR_ROOT)


from src.models import NewsDB, TrendMArticle
from src.modules.publisher.trend_m import TMPublisher, TMDriver, TMUserInfo

from src.utils import Env


sectors = dict()
not_published_article = TrendMArticle.select().where(TrendMArticle.published==False)
print(len(not_published_article))

n_sectors = len(set([article.data['sector'] for article in not_published_article]))

for article in not_published_article:
    sector = article.data['sector']
    if sector not in sectors.keys():

        sectors[sector] = [article]
    else:
        if len(sectors[sector]) < 20:
            sectors[sector].append(article)

    if all([ len(val) >= 20 for val in sectors.values()]) and len(sectors.keys())==n_sectors:
        break


articles = []
for key, val in sectors.items():
    print(key, len(val))
    articles.extend(val)

print(len(articles))

article_ids = list(map(lambda a: a.id, articles))

publisher = TMPublisher(
    user_info = TMUserInfo(
    email    = Env.get("TRENDM_ID"),
    password = Env.get("TRENDM_PASSWORD"), ))

publisher(article_ids)