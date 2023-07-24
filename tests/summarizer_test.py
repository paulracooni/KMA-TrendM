import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from tqdm import tqdm
from pprint import pprint
from models import GptResult
from modules.news_gpt import Determinator, Summarizer


q= GptResult.provider == Determinator().provider
q_determined = GptResult.select().where(GptResult.provider == Determinator().provider)

summarizer = Summarizer()

result_ids = []
for r in tqdm(q_determined):
    if r.data.get('suitable'):
        result_ids.append(summarizer(news_id=r.news.id))

query = GptResult.select().where(GptResult.id << result_ids)
usage = sum([ result.usage for result in query ])


print(f"""
[Summarizer test result]
# total      : {len(query)}
$ usage      : KRW {usage * 1200:.2f} won
""")

for summary in query:
    pprint(summary.data)
