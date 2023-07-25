import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import json
from time import sleep
from itertools import chain as it_chain
from models import News, TrendMArticle
from celery import chain, group
from tasks import (
    read_topics,
    read_keywords,
    crawling_news_en,
    crawling_news_kr,
    deduplicate,
    gpt_analysis,
    publish_trend_m
)

def wait_unitl_done(task, poll_time=5):
    while not task.ready(): sleep(poll_time)
    return task.join_native(propagate=False)



params = dict(propagate=False, disable_sync_subtasks=False)

# Crawlng task
task_collect_en = group(*( chain(
    crawling_news_en.s(topic),
    deduplicate.s(),)
for topic in read_topics()))

task_collect_kr = group(*(chain(
    crawling_news_kr.s(keyword, 5),
    deduplicate.s(),)
for keyword in read_keywords()))

res_tc_en = flatten_and_filter_type(
    task_collect_en.delay().join_native(**params), int)

res_tc_kr = flatten_and_filter_type(
    task_collect_kr.delay().join_native(**params), int)

news_ids = res_tc_en + res_tc_kr

# Analysis Task
task_analysis = group(*(
    gpt_analysis.s(news_id)
    for news_id in news_ids ))

result_ids = flatten_and_filter_type(
    task_analysis.delay().join_native(**params), int)

# Publish Task
tp = publish_trend_m.delay(result_ids)
tp.get(**params)