import sys
from pathlib import Path

sys.path.append(str(Path(__file__).parent.parent))


from tasks import crawling_news_kr


task = crawling_news_kr.delay("테스트", max_results=1)
result = task.get(propagate=False, disable_sync_subtasks=False)
print(result)
