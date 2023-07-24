from ..chatgpt import ChatGPT
from ..utils import get_prompt
from models import GptResult
from utils.logger import DbLogger
logger = DbLogger(__name__.split(".")[-1])

class GptClsTrendIssue(ChatGPT):
    __version__ = "230723"

    sys_prompt = get_prompt(__file__, "SYS_V2_CLASSIFY_TREND_ISSUE")

    json_format = {
        "trendPattern"       : str,
        "probsOfTrendPattern": {
            "enhancement" : str,
            "expansion"   : str,
            "connectivity": str,
            "disruption"  : str,
            "reduction"   : str,
            "reversal"    : str
        },
        "issue"       : str,
        "probsOfIssue": {
            "tech-centric"   : str,
            "culture"        : str,
            "type"           : str,
            "sense"          : str,
            "space"          : str,
            "ecosystem"      : str,
            "experience"     : str,
            "co-creation"    : str,
            "community"      : str,
            "personalization": str,
            "originality"    : str,
            "luxury"         : str,
            "environment"    : str,
            "time"           : str,
            "curation"       : str,
            "diversity"      : str,
            "subculture"     : str,
            "human-centric"  : str
        }
    }

    trend_issue_set = {
        "enhancement" : ["tech-centric", "culture", "type"],
        "expansion"   : ["sense", "space", "ecosystem"],
        "connectivity": ["experience", "co-creation", "community"],
        "disruption"  : ["personalization", "originality", "luxury"],
        "reduction"   : ["environment", "time", "curation"],
        "reversal"    : ["diversity", "subculture", "human-centric"]
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

        for key in ['probsOfTrendPattern', 'probsOfIssue']:
            self.check_json_keys(
                data_keys     = content[key].keys(),
                expected_keys = self.json_format[key].keys(),
                usage         = usage,
                news          = news,                         )
        
        for key_val, key_prob in [
            ("trendPattern", "probsOfTrendPattern"), 
            ("issue", "probsOfIssue")]:
            self.check_json_values(
                data   = content[key_val],
                values = self.json_format[key_prob].keys(),
                usage  = usage,
                news   = news,                                           )

        values = self.trend_issue_set[
            content["trendPattern"].lower()]

        self.check_json_values(
                data   = content["issue"].lower(),
                values = values,
                usage  = usage,
                news   = news,                     )

        return content, usage
    