import json
from os import walk
from time import time, sleep
from pathlib import Path
from pprint import pformat

from retry import retry

from models import NewsDB, GptResult
from utils import Env
from utils.logger import DbLogger
logger = DbLogger(__name__.split(".")[-1])

import openai
import tiktoken
from openai.error import (
    APIError, RateLimitError, ServiceUnavailableError, InvalidRequestError)
openai.api_key      = Env.get("OPENAI_API_KEY")
openai.organization = Env.get("OPENAI_ORGANIZATION")


def init_prompts():
    exts = ".txt"
    DIR_PROMPTS = Path(__file__).parent / 'prompts'

    names = [ file_name.replace(exts, '')
        for root, dirs, files in walk(DIR_PROMPTS)
        for file_name in files
        if file_name.endswith(exts) ] 
    
    read_file = lambda p : p.open("r", encoding="utf-8").read()

    return {
        name : read_file(DIR_PROMPTS / f"{name}{exts}")
        for name in names }


class ChatGPT:
    # Configs
    emb_model = 'text-embedding-ada-002'
    price_emb = 0.0000001

    gpt_model  = "gpt-3.5-turbo"
    max_token  = 4097
    price_in   = 0.0000015
    pricce_out = 0.000002
    
    temperature = 0.0
    prompts = init_prompts()

    debug = False
#region Abstract methods
    @property
    def provider(self):
        raise NotImplementedError
    
    def prep_user_prompt(self, input_data):
        raise NotImplementedError

    def run(self, user_prompt, news):
        raise NotImplementedError
    
    def check_content(self, content, usage, news):
        raise NotImplementedError
#endregion

#region GPT single request process
    # @retry(tries=1, delay=0)
    def __call__(self, input_data):

        user_prompt, news = self.prep_user_prompt(input_data)

        result = self.was_already_done(news)
        if not self.debug and result != None: return result
 
        st = time()
        content, usage = self.run(user_prompt, news)
        content, usage = self.check_content(content, usage, news)

        logger.info(
            f"{self.provider} End - Success",
            data=dict(usage=usage, news_id=news.id, exec_time=time() - st))
        
        result = self.save_result(news, content, usage)

        return result.id

    def was_already_done(self, news):

        w_news = GptResult.news==news
        w_prov = GptResult.provider==self.provider
        q_result = GptResult.select().where(w_news & w_prov)
        
        if q_result.exists():
            logger.info(f"{self.provider} End - Already exist", not_db=True)
            return q_result.get()
        
        return None
    
    def save_result(self, news, content, usage):
        with NewsDB._meta.database.atomic():
            result = GptResult.create(
                provider = self.provider,
                news     = news,
                data     = content,
                usage    = usage,         )
        return result
#endregion

#region openai requests
    @classmethod
    @retry(exceptions=(APIError, ServiceUnavailableError), tries=5, delay=5)
    @retry(exceptions=RateLimitError, tries=2, delay=60)
    def embedding(cls, content, as_vector=True):
        response = openai.Embedding.create(input=content, engine=cls.emb_model)
        return cls.as_vector(response) if as_vector else response 

    @classmethod
    @retry(exceptions=(APIError, ServiceUnavailableError), tries=5, delay=5)
    @retry(exceptions=RateLimitError, tries=2, delay=60)
    def create_completion(cls, system_prompt, user_prompt):
        return openai.ChatCompletion.create(
            model=cls.gpt_model,
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            temperature = cls.temperature,
        )
        
    @classmethod
    def as_content_and_usage(cls, response):
        token_in = response['usage']['prompt_tokens']
        token_out = response['usage']['completion_tokens']
        usage = (cls.price_in * token_in) + (cls.pricce_out * token_out)
        content = response['choices'][0]['message']['content']
        return content, usage
    
    @classmethod
    def as_vector_and_usage(cls, response):
        usage = response['usage']['total_tokens'] * cls.price_emb
        vector = response['data'][0]['embedding']
        return vector, usage
    
    @classmethod
    def as_vector(cls, response):
        return response['data'][0]['embedding']
#endregion

#region Utils
    @classmethod
    def cnt_tokens(cls, messages, model="gpt-3.5-turbo-0613"):
        """Return the number of tokens used by a list of messages."""
        try:
            encoding = tiktoken.encoding_for_model(model)
        except KeyError:
            encoding = tiktoken.get_encoding("cl100k_base")
        if model in {
            "gpt-3.5-turbo-0613",
            "gpt-3.5-turbo-16k-0613",
            "gpt-4-0314",
            "gpt-4-32k-0314",
            "gpt-4-0613",
            "gpt-4-32k-0613", }:
            tokens_per_message = 3
            tokens_per_name    = 1
        elif model == "gpt-3.5-turbo-0301":
            tokens_per_message = 4  # every message follows <|start|>{role/name}\n{content}<|end|>\n
            tokens_per_name    = -1  # if there's a name, the role is omitted
        elif "gpt-3.5-turbo" in model:
            return cls.cnt_tokens(messages, model="gpt-3.5-turbo-0613")
        elif "gpt-4" in model:
            return cls.cnt_tokens(messages, model="gpt-4-0613")
        else:
            raise NotImplementedError(
                f"num_tokens_from_messages() is not implemented for model {model}. "
                "See https://github.com/openai/openai-python/blob/main/chatml.md for "
                "information on how messages are converted to tokens."
            )
        num_tokens = 0
        for message in messages:
            num_tokens += tokens_per_message
            for key, value in message.items():
                num_tokens += len(encoding.encode(value))
                if key == "name":
                    num_tokens += tokens_per_name
        num_tokens += 3  # every reply is primed with <|start|>assistant<|message|>
        return num_tokens

    @classmethod
    def chunking_article(cls, article, system_prompt):

        chunks    = []
        chunk     = ""
        n_tokens  = 0
        article  = article.split("\n")

        for i, article_line in enumerate(article):
            
            temp_chunk = chunk + article_line

            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": temp_chunk}
            ]

            n_tokens = cls.cnt_tokens(messages, cls.gpt_model)

            if n_tokens < cls.max_token:
                chunk = temp_chunk
                if i == len(article)-1:
                    chunks.append(chunk)
            else:
                chunks.append(chunk)
                chunk = article_line

        return chunks
    
    @classmethod
    def guess_n_token(cls, system_prompt, user_prompt):
        return cls.cnt_tokens(
            messages = [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt}
            ],
            model=cls.gpt_model,)
    
    @classmethod
    def had_same_keys(cls, expected, actual):
        return set(expected) == set(actual)
    
    @classmethod
    def is_same_set(cls, expected, actual):
        return set(expected) == set(actual)
    
    @classmethod
    def check_json_format(cls, content, usage, news):
        try:
            content = json.loads(content)
        except json.decoder.JSONDecodeError as e:
            message = f"Invalid Json format responsed below:\n{pformat(content)}"
            logger.error(message, data=dict(usage=usage, news_id=news.id))
            raise e
        return content
    
    @classmethod
    def check_json_keys(cls, data_keys, expected_keys, usage, news):
        if not cls.is_same_set(data_keys, expected_keys):
            message = "Expected key is not in response"
            logger.error(message, data=dict(
                usage         = usage,
                news_id       = news.id,
                data_keys     = list(data_keys),
                expected_keys = list(expected_keys), ))
            raise ValueError(message)
    
    @classmethod
    def check_json_values(cls, data, values, usage, news):
        if not any([data.lower() == value.lower() for value in values]):
            message = "Expected value is not in response"
            logger.error(message, data=dict(
                usage   = usage,
                news_id = news.id,
                data    = data,
                values  = list(values),  ))
            raise ValueError(message)

#endregion