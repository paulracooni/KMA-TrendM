from ..chatgpt import ChatGPT
from ..utils import get_prompt
from src.models import GptResult
from src.utils.logger import DbLogger
logger = DbLogger(__name__.split(".")[-1])

class GptClsSector(ChatGPT):
    __version__ = "230723"

    sys_prompt = get_prompt(__file__, "SYS_V2_CLASSIFY_SECTOR")

    json_format = {
        "sector"       : str,
        "probsOfSector": {
            "marketing" : float,
            "branding"  : float,
            "lifestyle" : float,
            "business"  : float,
            "tech"      : float,
            "consumer"  : float,
            "contents"  : float,
            "design"    : float,
            "culture"   : float,
            "esg"       : float,
            "generation": float,
            "economy"   : float,
        },
    }

    
    @property
    def provider(self):
        return f"{self.gpt_model}-{self.__class__.__name__}-{self.__version__}"
    
    def prep_user_prompt(self, input_data):
        result_summary_id = input_data
        result = GptResult.select().where(
            GptResult.id==result_summary_id).get()
        news   = result.news
        summary = result.data.get('summary')
        user_prompt = f"{news.title}\n{summary}"
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

        expected_keys = self.json_format['probsOfSector'].keys()
        self.check_json_keys(
            data_keys     = content['probsOfSector'].keys(),
            expected_keys = expected_keys,
            usage         = usage,
            news          = news,                            )

        self.check_json_values(
            data   = content['sector'],
            values = expected_keys,
            usage  = usage,
            news   = news,              )

        return content, usage
    