from models import NewsDB, News, Image, GptResult, TrendMArticle
from ..determinator import GptDeterminator
from ..classifier import GptClsTrendIssue, GptClsSector
from ..summarizer import GptTitle, GptSummary, GptInsights, GptKeywords
from .task_checker import TaskChecker
from utils.logger import DbLogger
logger = DbLogger(__name__.split(".")[-1])


class TaskNewsAnalysis:

    template = "230719"

    def __init__(self, today):
        
        self.checker = TaskChecker(today)
        # determinator
        self.gpt_det = GptDeterminator()

        # summmarizer
        self.gpt_summary  = GptSummary()
        self.gpt_title    = GptTitle()
        self.gpt_insights = GptInsights()
        self.gpt_keywords = GptKeywords()

        # classifier
        self.gpt_cls_trend  = GptClsTrendIssue()
        self.gpt_cls_sector = GptClsSector()

        self.total_usage = 0

    def __call__(self, news_id):
        news = self.get_news(news_id)

        article = self.check_already_done(news)
        if article != None:
            return article.id

        # Check task was done
        is_determiated_done = self.checker.is_determiated_done(self.gpt_det)
        is_analysis_done = self.checker.is_analysis_done(self.gpt_cls_sector)

        if is_determiated_done or is_analysis_done: return None

        determined = self.determination(news)
        if not determined['suitable']: return None

        if is_analysis_done: return None
        
        summarized, result_summary_id = self.summarize(news)
        classified = self.classify(result_summary_id)
        article = self.create_trend_m_article(
            news, data={**determined, **summarized, **classified})

        return article.id

    def determination(self, news):
        res_det = self.get_result(self.gpt_det(news))
        return res_det.data

    def summarize(self, news): 
        res_summary  = self.get_result(self.gpt_summary(news))
        res_title    = self.get_result(self.gpt_title(res_summary.id))
        res_insights = self.get_result(self.gpt_insights(res_summary.id))
        res_keywords = self.get_result(self.gpt_keywords(res_summary.id))
        summarized = {
            **res_title.data,
            **res_summary.data,
            **res_insights.data,
            **res_keywords.data}
        return summarized, res_summary.id

    def classify(self, result_summary_id):
        res_trend  = self.get_result(self.gpt_cls_trend(result_summary_id))
        res_sector = self.get_result(self.gpt_cls_sector(result_summary_id))
        return {**res_trend.data, **res_sector.data,}

    def create_trend_m_article(self, news, data):

        image = Image.select().where(
            (Image.news==news)&(Image.is_top==True)).get()
        
        with NewsDB._meta.database.atomic():
            article = TrendMArticle.create(
                template      = self.template,
                news          = news,
                iamge         = image,
                data          = data,
                published     = False,
                published_url = None,     )
            article.image = image
            article.save()
        return article

    def check_already_done(self, news):
        q_article = TrendMArticle.select().where(TrendMArticle.news==news)
        if q_article.exists():
            return q_article.get()
        return None
    
    def get_news(self, news_id):
        news = News.get_by_id(news_id)
        if news == None:
            raise ValueError(f"Not exist news({news_id})")
        return news
    
    def get_result(self, result_id):
        result = GptResult.select().where(GptResult.id==result_id).get()
        self.total_usage += result.usage
        return result
    
    def raise_error(self, message, usage, news):
        log = logger.error(message, data=dict(usage=usage, news_id=news.id))
        raise RuntimeError(f"{message} - Log id {log.id}")