import traceback
import pytz
from datetime import datetime, timedelta
from dateutil import parser as dt_parser

from attrdict import AttrDict
from autoclass import autoargs

import re
import requests
from fake_useragent import UserAgent

from gnews import GNews

from utils.logger import get_logger
from .base_crawlers import BaseNewsCrawler

from models import *

logger = get_logger(__name__.split('.')[-1])


class CustomGnews(GNews):

    # Overriding
    def get_full_article(self, url):
        try:
            from newspaper import Article
            from newspaper import Config
            from fake_useragent import UserAgent

            config = Config()
            config.browser_user_agent = UserAgent(
                use_external_data=True, verify_ssl=True).random
            config.request_timeout = 20

            article = Article(url="%s" % url, language=self._language)
            article.download(recursion_counter=5)
            article.parse()
        except Exception as e:
            logger.error(f"{e} - {e.args[0]}")
            return None
        return article


class GoogleNewsCrawler(BaseNewsCrawler):
    country = 'US'
    language= 'en'
    topics = [
        "WORLD", "NATION", "BUSINESS", "TECHNOLOGY",
        "ENTERTAINMENT", "SPORTS", "SCIENCE", "HEALTH"
    ]

    def __init__(self):
        self.gnews = CustomGnews(language='en', country='US')
        self.tommorow, self.yesterday = self.init_dates()


    def crawling(self, keyword=None):
        topic = keyword.upper()
        assert topic in self.topics
        searched_news = self.search_news(topic)
        logger.info(f"End search_news based on topics, n={len(searched_news)}")

        news_objs = []
        for news in map(AttrDict, searched_news):
            try:
                article = self.get_full_article(url=self.get_url(news))
                if article == None: continue
                news_obj = self.build_news_obj(news, article)
                news_objs.append(news_obj)
                logger.info(f"Success, title={news.title}")
            except RuntimeError as e:
                logger.error(e)
            except Exception as e:
                logger.error(
                    f"{e}, url={self.get_url(news)}\n"
                    f"[Traceback]\n"
                    f"{traceback.format_exc()}")

        return news_objs

    def was_already_saved(self, news):
        is_exist_origin = News.select().where(
            News.url_origin==news['url_origin']).exists()

        is_exist = News.select().where(
            News.url==news['url']).exists()

        return is_exist_origin or is_exist

    def search_news(self, topic):

        news_temp = self.gnews.get_news_by_topic(topic)

        urls = []
        url_origins = []
        searched_news = []
        for n in news_temp:
            n['published_date'] = dt_parser.parse(n['published date'])
            n['url_origin'] = self.__req_url_origin(
                    url     = n['url'],
                    url_pub = n['publisher']['href'], )

            # filter already searched
            if n['url'] not in urls and n['url_origin'] not in url_origins:
                urls.append(n['url'])
                url_origins.append(n['url_origin'])
                searched_news.append(n)

        searched_news = list(filter(
            lambda n: self.yesterday<=n['published_date']<=self.tommorow, searched_news))

        # filter already exist
        searched_news = list(filter(self.was_already_saved, searched_news))

        searched_news = sorted(
            searched_news, key=lambda n: n['published_date'], reverse=True,)

        logger.info(f"search_news based on topic={topic}, n={len(news_temp)}")

        return searched_news

    def get_full_article(self, url):
        return self.gnews.get_full_article(url)
    
    def get_url(self, news):
        return news.url

    def build_news_obj(self, news, article):
        
        if not article.authors:
            raise RuntimeError(f"No Reporter - {news.url}")

        if not article.text:
            raise RuntimeError(f"No Article - {news.url}")

        date_pub = news['published_date'].strftime("%Y-%m-%d %H:%M:%S") \
            if isinstance(news['published_date'], datetime) \
            else datetime.now().strftime("%Y-%m-%d %H:%M:%S")

        images = [article.top_image] + [article.meta_img]
        images = images + list(article.images)
        images = [dict(url=image) for image in images]

        videos = [dict(url=video) for video in article.movies]

        return {
            "news": {
                "url"        : news.url,
                "url_origin" : news.url_origin,
                "title"      : article.title,
                "article"    : article.text,
                "description": news.description,
                "date_pub"   : date_pub,
                "country"    : self.country,
                "language"   : self.language,
            },
            "publisher": {
                "name": news.publisher.title,
                "url" : news.publisher.href,
            },
            "reporters": [article.authors[0]],
            "images"   : images,
            "videos"   : videos,
        }
    

    def __req_url_origin(self, url, url_pub):
        user_agent = UserAgent(use_external_data=True, verify_ssl=True).random
        response = requests.get(url=url, headers={"User-Agent": user_agent})
        urls = re.findall(r"\"https:\/\/(.*?)\"", response.text)
        urls = map(lambda url: f"https://{url}", urls)
        urls = list(filter(lambda url: url_pub in url, urls))
        return urls[0] if urls else None