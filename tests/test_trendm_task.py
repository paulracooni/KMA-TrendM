import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)
import sys; sys.path.append("/app")

import random
from datetime import datetime

from celery import group
from celery.result import GroupResult
from tasks import (
    read_keywords,
    read_topics,
    groupping,
    crawling_news_kr,
    crawling_news_en,
    flatten_and_filter_type,
    remove_dup_news,
    deduplicate,
    gpt_analysis,
    publish_trend_m
)

keywords = [
"사랑",
"상징",
"선언문",
"선호도",
]


def batch_group_run(task_func, params, n_batch=10, ret_type=int):

    batch_params = [
        
    ]

    futures = []
    for param in params:
        if isinstance(param, tuple):
            futures.append(task_func.delay(*param))
        else:
            futures.append(task_func.delay(param))

    results = []
    for future in futures:

        result = future.get(propagate=False, disable_sync_subtasks=False)

        if isinstance(result, list) and ret_type != list:
            result = list(filter(lambda r: isinstance(r, ret_type), result))
            results.append(result)

        elif isinstance(result, ret_type):
            results.append(result)

    return results


params = dict(propagate=False, disable_sync_subtasks=False)

today = datetime.now().strftime("%Y-%m-%d")
print(f"task_trendm.today={today}")

# Crawlng task
print(f"task_trendm start crawlng task")
task_collect_kr = groupping(crawling_news_kr, keywords, str)
res_tc_kr = task_collect_kr().join(**params)
# res_tc_kr = task_collect_kr.delay()
# res_tc_kr = res_tc_kr.join_native(**params)

# res_tc_en = group_run(crawling_news_en, read_topics(), int)
# task_collect_en = groupping(crawling_news_en, read_topics(), str)
# res_tc_en = task_collect_en().join(**params)
# res_tc_en = task_collect_en.delay()
# res_tc_en = res_tc_en.join_native(**params)
res_tc_en = []
# Delete duplicated News
print(f"task_trendm delete duplicated News")
removed_ids = flatten_and_filter_type(remove_dup_news(today), int)

res_collected = [
    list(filter(lambda id: id not in removed_ids, news_ids))
    for news_ids in list(res_tc_en) + list(res_tc_kr)
    if isinstance(news_ids, list)
]

# Delete simmilar News
print(f"task_trendm delete simmilar News")
task_deduplicate = groupping(deduplicate, res_collected, list)
news_ids = flatten_and_filter_type(task_deduplicate().join(**params), int)
# task_deduplicate = groupping(deduplicate, res_collected, list)
# news_ids = flatten_and_filter_type(
    # task_deduplicate.delay().join_native(**params), int)

news_ids = list(set(news_ids))
random.shuffle(news_ids)

# Analysis News
print(f"task_trendm analysis news")
task_analysis = group(*(gpt_analysis.s(news_id, today) for news_id in news_ids))
result_ids = flatten_and_filter_type(task_analysis().join(**params), int)
# task_analysis = group(*(gpt_analysis.s(news_id, today) for news_id in news_ids ))
# result_ids = flatten_and_filter_type(
    # task_analysis.delay().join_native(**params), int)

# Publish Task
print(f"task_trendm publish articles")