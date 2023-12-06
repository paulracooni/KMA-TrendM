import pyrootutils
project_root = pyrootutils.setup_root(__file__)
import sys; sys.path.append(str(project_root))

from pprint import pprint
from src.models import News, GptResult
from src.modules.news_gpt.summarizer.gpt_summary import GptSummary
from src.modules.news_gpt.summarizer.gpt_keywords import GptKeywords

# The summary characters must be between 600 to 800.
input_data = News(article="""
사과 네댓 개가 담긴 한 봉지에 만 5,900원 가격표가 붙었습니다.

할인 상품이라는 데 쉽게 담지 못하고 들었다 놓습니다.

[강춘옥/서울시 마포구 : "(사과를) 아침에 잘 먹는데 크기도 작아지고 개수도 많지 않은데 너무 많이 올랐네요. 사과하고 딸기는 정말 힘들어요, 사기가…"]

딸기 한 팩도, 감귤도 만 원을 훌쩍 넘는 가격입니다.

과일값 부담은 통계로도 나타나, 11월 신선과실 물가가 1년 전보다 25% 가까이 상승했습니다.

사과와 딸기, 감 등 제철을 맞은 과일이 더 많이 올랐습니다.

밥상에서 빠질 수 없는 대파 가격도 39%나 치솟았고 매일 먹는 쌀은 10% 넘게 올랐습니다.

전체 농산물 물가는 2년 6개월 만에 가장 큰 폭으로 상승했습니다.

[김인숙/서울시 양천구 : "대파가 많이 올랐어요. 옛날에는 2,500원 하던 게 지금은 5,000원이고요. 안 넣어 먹을 수는 없으니 적게 넣어 먹는 거죠."]

과일 가격은 단기간 내에 떨어지기 어려워 당분간 가계에 부담을 더할 것으로 보입니다.

다만 전체 소비자물가 상승률은 3.3%로 한 달 전보다 오름 폭이 줄었습니다.

석유류 가격이 하락한 영향입니다.

정부는 이에 따라 농수산물 할인 지원을 연장하는 등 주요 불안 품목을 겨냥해 물가를 관리한다는 계획입니다.

앞으로 물가는 안정세를 찾을 거라고 정부와 한국은행 모두 전망했는데, 국제 유가가 급등하거나 겨울철 기상 여건이 나빠지면 상황이 달라질 수 있다고 덧붙였습니다.

""")


gpt_summary = GptSummary()
gpt_keywords = GptKeywords()


summary = GptSummary()
content, usage = summary(input_data, return_as_content=True)


pprint(gpt_summary.sys_prompt_full)
news = News.select()[28]
print(news.url_origin)
result_id = gpt_summary(news)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)


pprint(gpt_keywords.sys_prompt)
result_id = gpt_keywords(result_id)
result = GptResult.select().where(GptResult.id==result_id).get()
pprint(result.data)

