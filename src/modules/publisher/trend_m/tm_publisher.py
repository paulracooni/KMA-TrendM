from selenium.common.exceptions import WebDriverException, TimeoutException
from src.models import NewsDB, TrendMArticle
from .tm_driver import TMDriver
from .renderer.renderer_230719 import render_template, _extr_valid_key

from src.utils.logger import get_logger
logger = get_logger(__name__.split('.')[-1])

class TMPublisher:

    def __init__(self, user_info):
        self.user_info = user_info

    def _init_driver(self):
        if not hasattr(self, 'driver'):

            self.driver = TMDriver(
                user_info = self.user_info,
                headless  = True,
                timeout   = 10)
            logger.info(f"TMPublisher.driver.initialized")
        if not self.driver.check_logined():
            self.driver.login()

            logger.info(f"TMPublisher.driver.login")

        # if hasattr(self, 'driver'):
        #     try:
        #         self.driver.driver.close()
        #         logger.info(f"TMPublisher.driver.close")
        #     except WebDriverException:
        #         logger.info(f"TMPublisher.driver.already_closed")

        # self.driver = TMDriver(
        #     user_info = self.user_info,
        #     headless  = True,
        #     timeout   = 10)

        # logger.info(f"TMPublisher.driver.initialized")
        # try:
        #     if not self.driver.check_logined():
        #         self.driver.login()
        # except TimeoutException:
        #     logger.info(f"TMPublisher.driver.login_error - retry")
        #     return self._init_driver()
        # logger.info(f"TMPublisher.driver.login")
        return self.driver



    def __call__(self, article_ids):
        self._init_driver()
        for article in TrendMArticle.select().where(TrendMArticle.id << article_ids):
            # if article.published: continue
            self.run(article)

    def run(self, article, retry=3):
        try:
            return self.__run(article)
        except Exception as e:
            import traceback
            logger.error(f"TMPublisher Error {e}\n{traceback.format_exc()}")
            self._init_driver()
            if not retry : 
                with NewsDB._meta.database.atomic(): 
                    article.published     = True
                    article.published_url = "ERROR"
                    article.save()
                return None
            self.run(article, retry=retry-1)
        
    def __run(self, article):
        # try:
        body_html = render_template(article)
        # except:
            # return None

        sector = _extr_valid_key(
            article.data, 'sector', 'probsOfSector').upper()

        self.driver.goto_page(sector)

        token, token_key = self.driver._make_token()

        article_url = self.driver._write_post(
            subject   = article.data['title'],
            body_html = body_html,
            image_url = article.image.url,
            token     = token,
            token_key = token_key,
            sector    = sector)

        logger.info(f"TMPublisher.published - {article_url}")

        with NewsDB._meta.database.atomic(): 
            article.published     = True
            article.published_url = article_url
            article.save()