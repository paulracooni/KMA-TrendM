import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import random

from datetime import datetime
from itertools import chain as it_chain

from celery import Celery
from celery import chain, group
from celery.schedules import crontab

from src.utils import Env
from src.utils.logger import DbLogger
from src.modules import Deduplicator, DupRemover, KeywordFilter
from src.modules.news_crawlers import GoogleNewsCrawler, NaverNewsCrawler
from src.modules.news_gpt.tasks import TaskNewsAnalysis
from src.modules.publisher.trend_m import TMUserInfo, TMPublisher


logger = DbLogger(__name__.split(".")[-1])

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
        crontab(hour=23, minute=5),
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

@celery.task(name="filtering_news", bind=True)
def filtering_news(self, news_ids):
    filter_by_keywords = KeywordFilter()
    return filter_by_keywords(news_ids)

@celery.task(name="remove_dup_news", bind=True)
def remove_dup_news(self, today=None):
    dup_remover = DupRemover(today)
    return dup_remover()

@celery.task(name="deduplicate", bind=True)
def deduplicate(self, news_ids, dup_th=0.9):
    deduplicator = Deduplicator(th=dup_th)
    return deduplicator(news_ids)

@celery.task(name="gpt_analysis", bind=True)
def gpt_analysis(self, news_id, today):
    task_analysis = TaskNewsAnalysis(today)
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
    logger.info(f"task_trendm.today={today}", not_db=True)

    # Crawlng task
    logger.info(f"task_trendm start crawlng task", not_db=True)
    task_collect_kr = groupping(crawling_news_kr, read_keywords(), str)
    res_tc_kr = task_collect_kr().join(**params)

    # 해외 뉴스는 제외, 한국어 뉴스만 수집
    # TODO: 추후 TRENDHUNTER 뉴스로 수집 예정
    # task_collect_en = groupping(crawling_news_en, read_topics(), str)
    # res_tc_en = task_collect_en().join(**params)

    # Filtering news
    logger.info(f"task_trendm delete need to filter News", not_db=True)
    task_filtering = groupping(filtering_news, res_collected, list)
    filtered_ids = flatten_and_filter_type(task_filtering().join(**params), int)
    
    # Delete duplicated News
    logger.info(f"task_trendm delete duplicated News", not_db=True)
    removed_ids = flatten_and_filter_type(remove_dup_news(today), int)
    
    res_collected = [
        list(filter(lambda id: id not in removed_ids + filtered_ids, news_ids))
        for news_ids in list(res_tc_kr) # list(res_tc_en) + list(res_tc_kr)
        if isinstance(news_ids, list)
    ]

    # Delete simmilar News
    logger.info(f"task_trendm delete simmilar News", not_db=True)
    task_deduplicate = groupping(deduplicate, res_collected, list)
    news_ids = flatten_and_filter_type(task_deduplicate().join(**params), int)
    # task_deduplicate = groupping(deduplicate, res_collected, list)
    # news_ids = flatten_and_filter_type(
        # task_deduplicate.delay().join_native(**params), int)

    news_ids = list(set(news_ids))
    random.shuffle(news_ids)

    # Analysis News
    logger.info(f"task_trendm analysis news", not_db=True)
    task_analysis = group(*(gpt_analysis.s(news_id, today) for news_id in news_ids ))
    result_ids = flatten_and_filter_type(task_analysis().join(**params), int)

    # Publish Task
    logger.info(f"task_trendm publish articles", not_db=True)
    tp = publish_trend_m(result_ids)

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

def group_run(task_func, params, ret_type=int):

    futures = []
    for param in params:
        if isinstance(param, tuple):
            futures.append(task_func.delay(*param))
        else:
            futures.append(task_func.delay(param))

    n_task = len(futures)
    logger.info(f"task_trendm create {n_task} tasks", not_db=True)

    results = []
    for i, future in enumerate(futures):

        result = future.get(propagate=False, disable_sync_subtasks=False)

        if isinstance(result, list) and ret_type != list:
            result = list(filter(lambda r: isinstance(r, ret_type), result))
            results.append(result)

        elif isinstance(result, ret_type):
            results.append(result)
     
        logger.info(f"task_trendm finish {i+1} of {n_task} tasks", not_db=True)

    return results
#endregion


