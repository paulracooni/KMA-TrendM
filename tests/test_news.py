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

params = dict(propagate=False, disable_sync_subtasks=False)
today = datetime.now().strftime("%Y-%m-%d")

# Crawlng task
print("# Crawlng task - Start")
task_collect_kr = groupping(crawling_news_kr, read_keywords(), str)
res_tc_kr = task_collect_kr.delay()
res_tc_kr = res_tc_kr.join_native(**params)

# task_collect_en = groupping(crawling_news_en, read_topics(), str)
# res_tc_en = task_collect_en.delay()
# res_tc_en = res_tc_en.join_native(**params)
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
task_deduplicate = groupping(deduplicate, res_collected, list)

news_ids = flatten_and_filter_type(
    task_deduplicate.delay().join_native(**params), int)

print(news_ids)
print("# Delete simmilar News - End")

news_ids = list(set(news_ids))
random.shuffle(news_ids)

# Analysis News
print("# Analysis News - Start")
task_analysis = group(*(gpt_analysis.s(news_id, today) for news_id in news_ids ))

result_ids = flatten_and_filter_type(
    task_analysis.delay().join_native(**params), int)
print(result_ids)
print("# Analysis News - End")


# Publish Task
print("# Publish Task - Start")
tp = publish_trend_m.delay(result_ids)
tp.get(**params)
print("# Publish Task - End")