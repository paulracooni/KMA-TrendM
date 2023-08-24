from ..chatgpt import ChatGPT
from ..utils import get_prompt
from src.models import GptResult
from src.utils.logger import DbLogger
logger = DbLogger(__name__.split(".")[-1])

class GptKeywords(ChatGPT):
    __version__ = "230723"

    sys_prompt = get_prompt(__file__, "SYS_V2_KEYWORD")
    json_format = {
        "keywords": [
        ]
    }
    @property
    def provider(self):
        return f"{self.gpt_model}-{self.__class__.__name__}-{self.__version__}"

    def prep_user_prompt(self, input_data):
        result_id = input_data # gpt summary result id
        result = GptResult.get_by_id(result_id)
        news = result.news
        user_prompt = (
            f"{news.title}\n"
            f"{result.data.get('summary')}\n")
        return user_prompt, news

    def run(self, user_prompt, news):
        return self.as_content_and_usage(
            self.create_completion(
                system_prompt = self.sys_prompt,
                user_prompt   = user_prompt, ))
    
    def check_content(self, content, usage, news):
        content = self.check_json_format(content, usage, news)
        self.check_json_keys(
            content.keys(), self.json_format.keys(), usage, news)
        
        content = {"keywords": content["keywords"]}
        return content, usage
    