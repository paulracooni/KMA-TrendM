import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)


from tasks import gpt_analysis
from models import News


st, et = 60, 70

for news in News.select()[st:et]:
    try:
        article_id = gpt_analysis(news.id)

    except Exception as e:
        print(news.title)
        print(news.url_origin)
        print(e)
        import traceback
        print(traceback.format_exc())
