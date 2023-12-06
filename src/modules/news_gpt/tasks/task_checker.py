
from src.models import News, GptResult

class TaskChecker:

    def __init__(self, today):

        self.max_detreminated          = 2000
        self.max_analysis              = 800
        self.max_analysis_per_category = 20

        self.news = News.select().where(News.date_get == today)

    def is_determiated_done(self, gpt_det):

        query = GptResult.select().where((
            GptResult.news << self.news) & (
            GptResult.provider == gpt_det.provider))
        
        n_suitable = sum([result.data['suitable'] for result in query])

        return n_suitable >= self.max_detreminated
    
    def is_analysis_done(self, gpt_cls_sector):

        query = GptResult.select().where((
            GptResult.news << self.news) & (
            GptResult.provider == gpt_cls_sector.provider))
        
        counter = {
            "marketing" : 0,
            "branding"  : 0,
            "lifestyle" : 0,
            "business"  : 0,
            "tech"      : 0,
            "consumer"  : 0,
            "contents"  : 0,
            "design"    : 0,
            "culture"   : 0,
            "esg"       : 0,
            "generation": 0,
            "economy"   : 0,
        }
        for result in query:
            key = result.data["sector"].lower()
            if key in counter.keys():
                counter[key] += 1


        all_count = sum(list(counter.values()))

        is_max_all = all_count >= self.max_analysis
        is_max_per_category = all([
            val >= self.max_analysis_per_category
            for val in counter.values()])

        return is_max_all or is_max_per_category
            
    

        # 5 * 4 = 20 * 120