import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from tqdm import tqdm
from models import GptResult
from modules.news_gpt import Summarizer, ClassifierV2

classifier = ClassifierV2()

result_ids = []
for result in tqdm(GptResult.select().where(GptResult.provider==Summarizer().provider)):
    result_ids.append(classifier(result_id=result.id))

query = GptResult.select().where(GptResult.id << result_ids)
usage = sum([ result.usage for result in query ])


print(f"""
[ClassifierV2 test result]
# total      : {len(query)}
$ usage      : KRW {usage * 1200:.2f} won
""")


{
    "usage": 0.0039534999999999995,
    "news_id": 186, 
    "data": "Education",
    "values": [
        "marketing",
        "branding",
        "lifestyle",
        "business", "tech", "consumer", "contents", "design", "culture", "esg", "generation", "economy"]}