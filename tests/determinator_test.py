import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from modules.news_gpt import Determinator
from tqdm import tqdm
from models import News, GptResult

st = 10
et = 20
determinator = Determinator()

result_ids = []
for news in tqdm(News.select()[st:et]):
    result_ids.append(determinator(news.id))


query = GptResult.select().where(GptResult.id << result_ids)
usage = sum([ result.usage for result in query ])


suitable = sum([ result.data['suitable'] for result in query ])

print(f"""
[Determinator test result]
# total      : {len(query)}
$ usage      : KRW {usage*1200:.2f} won
# suitalbe   : {suitable}
% shutability: {(suitable/len(query))*100:.2f} %
""")

