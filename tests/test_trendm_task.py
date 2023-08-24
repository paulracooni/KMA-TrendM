import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)
import sys; sys.path.append("/app")

import random
from datetime import datetime

from celery import group

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
"도전",
"독창적",
"독특한",
"동향",
]


def group_run(task_func, params, ret_type=int):

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

# Crawlng task
print("# Crawlng task - Start")
res_tc_kr = group_run(crawling_news_kr, keywords, int)

res_tc_en = []
print(res_tc_kr)
print(res_tc_en)
print("# Crawlng task - End")

# Delete duplicated News
print("# Delete duplicated News - Start")
removed_ids = flatten_and_filter_type(
    remove_dup_news.delay(today).get(**params), int)

res_collected = [
    list(filter(lambda id: id not in removed_ids, news_ids))
    for news_ids in list(res_tc_en) + list(res_tc_kr)
    if isinstance(news_ids, list)
]

print(removed_ids)
print(res_collected)
print("# Delete duplicated News - End")

# Delete simmilar News
print("# Delete simmilar News - Start")
# task_deduplicate = groupping(deduplicate, res_collected, list)
news_ids = group_run(deduplicate, res_collected, int)
news_ids = flatten_and_filter_type(news_ids, int)
print(news_ids)
print("# Delete simmilar News - End")

news_ids = list(set(news_ids))
random.shuffle(news_ids)

# Analysis News
print("# Analysis News - Start")
# task_analysis = group(*(gpt_analysis.s(news_id, today) for news_id in news_ids ))
news_ids = map(lambda news_id: (news_id, today), news_ids)
result_ids = group_run(gpt_analysis, news_ids, int)
result_ids = flatten_and_filter_type(result_ids, int)
print(result_ids)
print("# Analysis News - End")


# Publish Task
print("# Publish Task - Start")
tp = publish_trend_m.delay(result_ids)
tp.get(**params)
print("# Publish Task - End")