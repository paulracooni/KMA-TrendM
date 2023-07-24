import pyrootutils
DIR_ROOT = pyrootutils.setup_root(__file__)

from tqdm import tqdm
from models import GptResult
from modules.news_gpt import Summarizer, Classifier
provider = 'gpt-3.5-turbo-Summarizer-230719'

classifier = Classifier()

result_ids = []
for result in tqdm(GptResult.select().where(GptResult.provider==Summarizer().provider)):
    result_ids.append(classifier(result_id=result.id))

query = GptResult.select().where(GptResult.id << result_ids)
usage = sum([ result.usage for result in query ])


print(f"""
[Classifier test result]
# total      : {len(query)}
$ usage      : KRW {usage * 1200:.2f} won
""")

{
    "data_keys"    : ["trendPattern", "probsOfTrendPattern", "issue", "probsOfIssue"],
    "expected_keys": ["trendPattern", "probsOfTrendPattern", "issue", "ProbsOfIssue"]
}