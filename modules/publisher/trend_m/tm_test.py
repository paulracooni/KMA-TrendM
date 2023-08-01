import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import sys
sys.path.append("/app")

from utils import Env
from models import TrendMArticle
from modules.publisher.trend_m.tm_user_info import TMUserInfo
from modules.publisher.trend_m.tm_publisher import TMPublisher

article = TrendMArticle.select().where(TrendMArticle.published==False).get()

print(article)

publisher = TMPublisher(
    user_info = TMUserInfo(
        email    = Env.get("TRENDM_ID"),
        password = Env.get("TRENDM_PASSWORD"), ))


publisher([article.id])

# python modules/publisher/trend_m/tm_test.py