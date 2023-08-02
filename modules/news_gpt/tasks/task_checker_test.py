import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)
from time import time
from datetime import datetime
from modules.news_gpt.tasks import TaskChecker
from modules.news_gpt.determinator import GptDeterminator
from modules.news_gpt.classifier import GptClsSector



today = datetime.strptime("2023-08-01", "%Y-%m-%d")
gpt_det = GptDeterminator()
gpt_cls_sector = GptClsSector()


checker = TaskChecker(today)

st = time()
is_determiated_done = checker.is_determiated_done(gpt_det)
print(f"exec_time={time()-st:.2f} sec, {is_determiated_done=}")

st = time()
is_analysis_done = checker.is_analysis_done(gpt_cls_sector)
print(f"exec_time={time()-st:.2f} sec, {is_analysis_done=}")