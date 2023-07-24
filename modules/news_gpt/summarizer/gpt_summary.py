from ..chatgpt import ChatGPT
from ..utils import get_prompt

from utils.logger import DbLogger
logger = DbLogger(__name__.split(".")[-1])

class GptSummary(ChatGPT):
    __version__ = "230723"

    sys_prompt_chunk = get_prompt(__file__, "SYS_V2_SUMMARIZE_CHUNK")
    sys_prompt_full  = get_prompt(__file__, "SYS_V2_SUMMARIZE_FULL")

    @property
    def provider(self):
        return f"{self.gpt_model}-{self.__class__.__name__}-{self.__version__}"
    
    def prep_user_prompt(self, input_data):
        # input_data: News
        news        = input_data
        user_prompt = news.article
        return user_prompt, news
    
    def run(self, user_prompt, news):
        n_token = self.guess_n_token(self.sys_prompt_full, user_prompt)
        if n_token < self.max_token - 300: # pad for error
            content, usage = self.summary_short(user_prompt)
        else:
            content, usage = self.summary_long(user_prompt)
        return content, usage

    def check_content(self, content, usage, news):
        content = {"summary": content}
        return content, usage
    
    def summary_short(self, user_prompt):
        return self.as_content_and_usage(
            self.create_completion(
                system_prompt = self.sys_prompt_full,
                user_prompt   = user_prompt, ))

    def summary_long(self, user_prompt):

        chunks = self.chunking_article(
            user_prompt, system_prompt=self.sys_prompt_chunk)
        
        contents = [
            self.as_content_and_usage(
                self.create_completion(
                    system_prompt = self.sys_prompt_chunk,
                    user_prompt   = chunk))
            for chunk in chunks ]
        
        new_user_prompt = "".join([r[0] for r in contents])
        usage = sum([r[1] for r in contents])

        content, usage_= self.as_content_and_usage(
            self.create_completion(
                system_prompt = self.sys_prompt_full,
                user_prompt   = new_user_prompt))
        usage += usage_

        return content, usage