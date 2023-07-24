import pytz
from datetime import datetime, timedelta
from models import *

class BaseNewsCrawler:

    def init_dates(self):

        dt = datetime.now() + timedelta(days=1)
        tommorow = datetime(
            year   = dt.year,
            month  = dt.month,
            day    = dt.day,
            tzinfo = pytz.UTC)

        dt = datetime.now() - timedelta(days=1)
        yesterday = datetime(
            year   = dt.year,
            month  = dt.month,
            day    = dt.day,
            tzinfo = pytz.UTC)

        return tommorow, yesterday
    
    def __call__(self, keyword):
        news_objs = self.crawling(keyword)
        saved_news = self.save(news_objs)
        return saved_news

    def crawling(self, keyword):
        raise NotImplementedError
    
    def save(self, news_objs):
        saved_news = []
        for news_obj in news_objs:
            news, created = self.__save(news_obj)
            if created:
                saved_news.append(news)
        return saved_news

    def __save(self, news_obj):
        with NewsDB._meta.database.atomic():
            # Save publisher
            publisher, created = Publisher.get_or_create(
                **news_obj['publisher'])
            publisher.save()

            # Save news
            news, created = News.get_or_create(
                publisher = publisher, **news_obj['news'], )
            
            if not created:
                return news, created

            # Save reporters
            for i, reporter_name in enumerate(news_obj['reporters']):
                reporter, _ = Reporter.get_or_create(
                    name=reporter_name, publisher=publisher, )
                reporter.save()

                rel_reporter, _ = RelNewsReporter.get_or_create(
                    news=news, reporter=reporter,)
                rel_reporter.save()

            # Save images
            for i, image in enumerate(news_obj['images']):
                image, _ = Image.get_or_create(
                    **image, is_top=not i, news=news)
                image.save()
            
            # Save vedeos
            for i, video in enumerate(news_obj['videos']):
                video, _ = Video.get_or_create(
                    **video, is_top=not i, news=news)
                image.save()

            return news, created