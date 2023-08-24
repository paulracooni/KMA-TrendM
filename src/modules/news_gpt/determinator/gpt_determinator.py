from ..chatgpt import ChatGPT
from ..utils import get_prompt
from src.models import NewsDB, GptResult, Image
from src.utils.logger import DbLogger
logger = DbLogger(__name__.split(".")[-1])

class GptDeterminator(ChatGPT):
    __version__ = "230723"

    sys_prompt = get_prompt(__file__, "SYS_V2_DETERMINE_230802")
    th_suitable = 0.85
    json_format = {
        "suitable"   : bool,
        "suitability": float,
        "reason"     : str
    }

    @property
    def provider(self):
        return f"{self.gpt_model}-{self.__class__.__name__}-{self.__version__}"
    
    def prep_user_prompt(self, input_data):
        news = input_data
        article = list(filter(bool, news.article.split("\n")))[:3]
        user_prompt = f"{news.title}\n{article}"
        return user_prompt, news

    def run(self, user_prompt, news):

        content = self.check_top_image(news)
        if content != None:
            raise RuntimeError("No top image news article")
        
        return self.as_content_and_usage(
            self.create_completion(
                system_prompt = self.sys_prompt,
                user_prompt   = user_prompt, ))
    
    def check_content(self, content, usage, news):

        content = self.check_json_format(content, usage, news)

        self.check_json_keys(content.keys(), self.json_format.keys(), usage, news)

        if isinstance(content['suitable'], str):
            content['suitable'] = {
                "TRUE":True, "FALSE":False}.get(
                    content['suitable'].upper(), content['suitable'])

        if not isinstance(content['suitability'], float):
            content['suitability'] = float(content['suitability'])

        if content['suitable'] and content['suitability'] < self.th_suitable:
            content['suitable'] = False

        if not isinstance(content['suitable'], bool):
            message = "Not expected value type(bool)"
            logger.error(message, data=dict(usage=usage, news_id=news.id))
            raise ValueError(message)

        return content, usage
    
    def check_top_image(self, news):
        q_image = (Image.select().where(
            (Image.news == news)&(Image.is_top==True)))
        
        if not q_image.exists():
            with NewsDB._meta.database.atomic():
                result = GptResult.create(
                    provider = self.provider,
                    news     = news,
                    data     = dict(
                        suitable = False,
                        reason   = "No top image.", ), )
        else:
            result = None
        return result