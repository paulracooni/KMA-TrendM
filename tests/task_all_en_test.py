import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

import json
from time import sleep
from itertools import chain as it_chain
from src.models import News, TrendMArticle
from celery import chain, group
from tasks import (
    read_topics,
    crawling_news_en,
    deduplicate,
    gpt_analysis,
    publish_trend_m
)

def wait_unitl_done(task, poll_time=5):
    while not task.ready(): sleep(poll_time)
    return task.join_native(propagate=False)

def flatten_and_filter_type(ids, type=int):
    if ids and isinstance(ids, list) and isinstance(ids[0], list):
        ids = list(it_chain.from_iterable(ids))
    ids = list(filter(lambda id: isinstance(id, type), ids))
    return ids

params = dict(propagate=False, disable_sync_subtasks=False)

task_collect_en = group(*( chain(
    crawling_news_en.s(topic),
    deduplicate.s(),)
for topic in read_topics()))

res_tc = task_collect_en.delay()

news_ids = res_tc.join_native(**params)
print("res_tc.join_native(**params) /////////////////////////////")
print(len(news_ids))
print(news_ids)
news_ids = flatten_and_filter_type(news_ids)
print("news_ids = flatten_and_filter_type(news_ids) /////////////////////////////")
print(len(news_ids))
print(news_ids)

task_analysis = group(*[
    gpt_analysis.s(news_id)
for news_id in news_ids])

res_ta = task_analysis.delay()

result_ids = res_ta.join_native(**params)
print("result_ids = res_ta.join_native(**params) /////////////////////////////")
print(len(result_ids))
print(result_ids)
result_ids = flatten_and_filter_type(result_ids)
print("result_ids = flatten_and_filter_type(result_ids) /////////////////////////////")
print(len(result_ids))
print(result_ids)

tp = publish_trend_m.delay(result_ids)
tp.get(**params)