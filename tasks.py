import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)
from datetime import datetime
from itertools import chain as it_chain

from celery import Celery
from celery import chain, group
from celery.schedules import crontab

from utils import Env
from modules import Deduplicator, DupRemover
from modules.news_crawlers import GoogleNewsCrawler, NaverNewsCrawler
from modules.news_gpt.tasks import TaskNewsAnalysis
from modules.publisher.trend_m import TMUserInfo, TMPublisher



def read_keywords():
    path_txt = DIR_ROOT / "data/input/keywords.txt"

    with path_txt.open("r", encoding='utf-8') as f:
        keywords = [
            keyword.replace("\n", "")
            for keyword in f.readlines() ]
    return keywords

def read_topics():
    path_txt = DIR_ROOT / "data/input/topics.txt"

    with path_txt.open("r", encoding='utf-8') as f:
        keywords = [
            keyword.replace("\n", "")
            for keyword in f.readlines() ]
    return keywords

#region Celery configure
celery  = Celery(
    __name__,
    broker                             = Env.get('CELERY_BROKER'),
    backend                            = Env.get('CELERY_BACKEND'),
    broker_connection_retry            = True,
    broker_connection_retry_on_startup = True,
    broker_connection_max_retries      = 10, )

celery.conf.timezone = 'Asia/Seoul'
celery.autodiscover_tasks()

@celery.on_after_configure.connect
def setup_periodic_tasks(sender, **kwargs):
    sender.add_periodic_task(
        crontab(hour=0, minute=0),
        task_trendm.s(), )
#endregion


#region Celery task define
@celery.task(name="my_add", bind=True)
def my_add(self, a, b):
    return a + b

@celery.task(name="crawling_news_en", bind=True)
def crawling_news_en(self, topic):
    crawler = GoogleNewsCrawler()
    saved_news = crawler(topic)
    return [news.id for news in saved_news]

@celery.task(name="crawling_news_kr", bind=True)
def crawling_news_kr(self, keyword, max_results=5):
    crawler = NaverNewsCrawler(max_results=max_results)
    saved_news = crawler(keyword)
    return [news.id for news in saved_news]

@celery.task(name="remove_dup_news", bind=True)
def remove_dup_news(self, today=None):
    dup_remover = DupRemover(today)
    return dup_remover()

@celery.task(name="deduplicate", bind=True)
def deduplicate(self, news_ids, dup_th=0.9):
    deduplicator = Deduplicator(th=dup_th)
    return deduplicator(news_ids)

@celery.task(name="gpt_analysis", bind=True)
def gpt_analysis(self, news_id):
    task_analysis = TaskNewsAnalysis()
    return task_analysis(news_id=news_id)


@celery.task(name="publish_trend_m", bind=True)
def publish_trend_m(self, article_ids):

    ids = clean_and_filter_ids(article_ids)
    if not ids: return None

    publisher = TMPublisher(
        user_info = TMUserInfo(
            email    = Env.get("TRENDM_ID"),
            password = Env.get("TRENDM_PASSWORD"), ))

    publisher(article_ids)

def clean_and_filter_ids(ids):
    if ids and isinstance(ids, list) and isinstance(ids[0], list):
        ids = list(it_chain.from_iterable(ids))
    return list(filter(lambda id: id != None , ids))
#endregion


#region Workflows
@celery.task(name="task_trendm", bind=True)
def task_trendm(self, ):

    params = dict(propagate=False, disable_sync_subtasks=False)
    
    today = datetime.now().strftime("%Y-%m-%d")

    # Crawlng task
    task_collect_en = groupping(crawling_news_en, read_topics(), str)
    task_collect_kr = groupping(crawling_news_kr, read_keywords(), str)
    
    res_tc_en = task_collect_en.delay()
    res_tc_kr = task_collect_kr.delay()

    res_tc_en = res_tc_en.join_native(**params)
    res_tc_kr = res_tc_kr.join_native(**params)

    # Delete duplicated News
    removed_ids = flatten_and_filter_type(
        remove_dup_news.delay(today).get(**params), int)

    res_collected = [
        list(filter(lambda id: id not in removed_ids, news_ids))
        for news_ids in list(res_tc_en) + list(res_tc_kr)
        if isinstance(news_ids, list)
    ]

    # Delete simmilar News
    task_deduplicate = groupping(deduplicate, res_collected, list)

    news_ids = flatten_and_filter_type(
        task_deduplicate.delay().join_native(**params), int)

    # Analysis News
    task_analysis = group(*(
        gpt_analysis.s(news_id)
        for news_id in news_ids ))

    result_ids = flatten_and_filter_type(
        task_analysis.delay().join_native(**params), int)

    # Publish Task
    tp = publish_trend_m.delay(result_ids)
    tp.get(**params)

def groupping(task, iterable, data_type=None):
    signatures = []
    for data in iterable:
        if data_type == None or isinstance(data, data_type):
            signatures.append(task.s(data))
    return group(*signatures)


def flatten_and_filter_type(ids, type=int):
    if ids and isinstance(ids, list) and isinstance(ids[0], list):
        ids = list(it_chain.from_iterable(ids))
    ids = list(filter(lambda id: isinstance(id, type), ids))
    return ids

#endregion


