import traceback
from time import sleep
from datetime import datetime

from pathlib import Path
from urllib.parse import urlparse

from attrdict import AttrDict
from autoclass import autoargs
from dateutil import parser as dt_parser

import requests
import bs4
from bs4 import BeautifulSoup
from fake_useragent import UserAgent


from utils import Env
from utils.logger import get_logger
from .base_crawlers import BaseNewsCrawler

from models import *

logger = get_logger(__name__.split('.')[-1])


class NaverNewsCrawler(BaseNewsCrawler):
    pad_time = 0.1
    @autoargs
    def __init__(self, max_results=100):
        self.language = "kr"
        self.country = "KR"

        self.tommorow, self.yesterday = self.init_dates()


    def crawling(self, keyword):

        searched_news = self.search_news(keyword)
        logger.info(f"search_news, keyword={keyword}, n={len(searched_news)}")

        news_objs = []
        for news in map(AttrDict, searched_news):
            try:
                article = self.get_full_article(url=self.get_url(news))
                news_obj = self.build_news_obj(news, article)
                news_objs.append(news_obj)
                logger.info(f"Success, keyword={keyword}, title={news.title}")
            except RuntimeError as e:
                logger.error(e)
            except Exception as e:
                logger.error(
                    f"{e}, keyword={keyword}, url={self.get_url(news)}\n"
                    f"[Traceback]\n"
                    f"{traceback.format_exc()}")

        return news_objs

    def search_news(self, keyword):

        items = dict()
        # 키워드당 최대 1000개까지만 검색 가능함
        for start in range(1, 1002, 100):

            start = start if start <= 1000 else 1000

            # Start 기준 Pagenated request 호출
            search_results = self.__search_news(keyword, start=start)
            if search_results == None:
                break
            
            # 중복된 기사 필터링
            search_results['items'] = list(filter(
                lambda n: not self.is_exist(
                    url        = n['link'].strip(),
                    url_origin = n['originallink'].strip(),
                    title      = n['title'].strip(),
                ),
                search_results['items'],)
            )
            
            # TODO: 연예 기사 필터링 - 현재는 해당 페이지가 Block 됨
            search_results['items'] = list(filter(
                self.__is_not_entertain,
                search_results['items'], ))

            # pubDate type 변경 as datetime
            for item in search_results['items']:
                item['pubDate'] = dt_parser.parse(item['pubDate'])

            # title cleaning
            for item in search_results['items']:
                item['title'] = clean_text(item['title'])

            # period 설정이 되어 있는 경우
            if self.yesterday != None:
                # Outdated 기사 필터링
                search_results['items'] = list(filter(
                    lambda n: self.yesterday<=n['pubDate']<=self.tommorow,
                    search_results['items'],))

            for item in search_results['items']:
                key = urlparse(item['link']).path
                item['url'] = item['link']
                items[key] = item
            
            # max_results 이상인 경우 검색 중지
            if self.max_results!=None and len(items) > self.max_results:
                break

            sleep(self.pad_time)

        # 최신순으로 정렬
        items = sorted(list(items.values()),
            key     = lambda x: x['pubDate'],
            reverse = True,                   )
        
        # 최대 검색결과 제한
        if self.max_results != None:
            return items[:self.max_results]

        return list(map(AttrDict, items))
    
    def __search_news(self, keyword, start=1):

        response =  requests.get(
            url     = 'https://openapi.naver.com/v1/search/news.json',
            headers = {
                "X-Naver-Client-Id"    : Env.get("NAVER_CLIENT_ID"),
                "X-Naver-Client-Secret": Env.get("NAVER_CLIENT_SECRET"),
            },
            params = dict(
                query   = keyword,
                display = 100,
                start   = start,
                sort    = 'sim' 
            )
        )
        
        if response.status_code == 429:
            logger.error("NAVER-Search-API-Err-429: Naver search api limit exclude ")
            return None
        elif response.status_code != 200:
            return None
        
        # TODO: When not status 200
        search_results = response.json()
        
        # News settings
        edited_items = []
        for news in search_results['items']:

            # Filter only naver news
            parsed_link = urlparse(news['link'])
            if not {"n.news.naver.com": True}.get(
                parsed_link.netloc, False):
                continue

            # Build url to request naver bot summary.
            news['linkSummary'] = "https://tts.news.naver.com/article/{}/summary".format(
                "/".join(parsed_link.path.split("/")[-2:]))

            edited_items.append(news)
        
        search_results['items'] = edited_items
        return search_results

    def __is_not_entertain(self, item):
        code = urlparse(item['link']).query.split('=')[-1]
        if not code:
            return False
        return int(code) != 106

    def get_full_article(self, url):
        # Request news
        user_agent = UserAgent(use_external_data=True, verify_ssl=True).random

        response = requests.get(
            url, headers={"User-Agent": user_agent})

        if response.status_code != 200:
            raise RuntimeError(f"{response.status_code} - {response.text}")

        # parse news
        soup = BeautifulSoup(response.text, 'html.parser')

        title = soup.select("#title_area > span")[0].text
        publisher = soup.select("#ct > div.media_end_head.go_trans > div.media_end_head_top > a > img")[0].attrs.get("title", "")
        publisher_url = soup.select("#ct > div.media_end_head.go_trans > div.media_end_head_top > a")[0].attrs.get("href", "")
        reporters = [reporter.text for reporter in soup.select("#contents > div.byline > p > span")]
        article, images = parse_article(soup.select("#dic_area")[0])

        # Build 
        return AttrDict(dict(
            title         = clean_text(title),
            publisher     = str(publisher),
            publisher_url = str(publisher_url),
            reporters     = reporters,
            article       = clean_text(article),
            images        = images,
        ))

    def get_url(self, news):
        return news['link']
    
    def build_news_obj(self, news, article):
        
        return {
            "news": {
                "url"        : news.link.strip(),
                "url_origin" : news.originallink.strip(),
                "title"      : article.title.strip(),
                "article"    : article.article,
                "description": news.description,
                "date_pub"   : news.pubDate.strftime("%Y-%m-%d %H:%M:%S"),
                "date_get"   : datetime.now().strftime("%Y-%m-%d"),
                "country"    : self.country,
                "language"   : self.language,
            },
            "publisher": {
                "name": article.publisher.strip(),
                "url" : article.publisher_url.strip(),
            },
            "reporters": article.reporters,
            "images"   : article.images,
            "videos"   : [],
        }

# //////////////////////////////////////////////////////////////////////////////
# Naver news (default parser)
# //////////////////////////////////////////////////////////////////////////////
def parse_article(article_body):

    article = ''
    images = []
    for ab in article_body:

        # HTML 주석
        if isinstance(ab, bs4.Comment):
            continue
        
        # 기사 원문
        elif isinstance(ab, bs4.element.NavigableString):
            
            text = str(ab.string).strip()
            if not text: continue
            article += f"{str(text)}\n\n"
        
        # 이미지
        elif ab.find_all("img"):

            herf, desc = "", str(ab.text).strip()
            for img in ab.find_all("img"):
                herf = str(img.attrs.get("data-src"))

            images.append(dict(url=herf, description=desc))

        # 기사 헤더
        elif ab.name in ["strong", "b"]:
            article += f"{str(text)}\n---\n\n"

        # 문단의 제목
        elif "style" in ab.attrs.keys():
            article += f"\n# {str(text)}\n\n"

        # 미분류 패턴
        elif ab.text:
            article += f"{str(text)}\n\n"
    
    return article, images

def clean_text(text):
    text = remove_iso_8559_1(text)
    text = remove_html_tag(text)
    return text

def remove_iso_8559_1(text):
    letter_set = {
        "&amp;" : "&",
        "&quot;": "\"",
        "&apos;": "\'",
        "&lt;"  : "<",
        "&gt;"  : ">"
    }
    for letter, replacer in letter_set.items():
        text = text.replace(letter, replacer)
    return text

def remove_html_tag(text):
    return BeautifulSoup(text, "lxml").text