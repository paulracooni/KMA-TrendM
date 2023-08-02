import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import sys
sys.path.append("/app")

from utils import Env
from models import TrendMArticle
from modules.publisher.trend_m.tm_user_info import TMUserInfo
from modules.publisher.trend_m.tm_publisher import TMPublisher


query = TrendMArticle.select().where(TrendMArticle.published==False)
article_ids = [ a.id for a in query ]

print(len(query))

publisher = TMPublisher(
    user_info = TMUserInfo(
        email    = Env.get("TRENDM_ID"),
        password = Env.get("TRENDM_PASSWORD"), ))

publisher(article_ids)

# python modules/publisher/trend_m/tm_test.py
