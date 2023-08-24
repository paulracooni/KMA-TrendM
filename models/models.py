from peewee import *
from playhouse.postgres_ext import *

from utils import Env
from models.databases import NewsDB

# from psycopg2.extras import Json
# from psycopg2.extensions import register_adapter
# register_adapter(dict, Json)

class Publisher(NewsDB):
    id   = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    name = CharField(column_name='name', verbose_name='신문사 이름', max_length=256, )
    url  = TextField(column_name='url', verbose_name='링크')

class News(NewsDB):
    id          = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    url        = TextField(column_name='url', verbose_name='링크', index=True)
    url_origin = TextField(column_name='urlOrigin', verbose_name='원본링크', null=True, index=True)

    title       = CharField(column_name='title', verbose_name='제목', max_length=256, )
    description = TextField(column_name='description', verbose_name='설명', null=True, )

    publisher = ForeignKeyField(column_name='publisher', verbose_name='신문사', model=Publisher)

    article = TextField(column_name='article', verbose_name='기사', null=True)

    country = FixedCharField(column_name='country', verbose_name='국가', max_length=2)
    language = FixedCharField(column_name='language', verbose_name='언어', max_length=2)

    date_pub  = DateTimeField(column_name='datePub', verbose_name='게시일', formats='%Y-%m-%d %H:%M:%S')
    date_get  = DateTimeField(column_name='dateGet', verbose_name='수집일', formats='%Y-%m-%d', index=True)


class Image(NewsDB):
    id          = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    url         = TextField(column_name='url', verbose_name='링크')
    description = TextField(column_name='description', verbose_name='설명', null=True, )
    is_top      = BooleanField(column_name='isTop', verbose_name='대표 이미지', default=False)
    news        = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News)

class Video(NewsDB):
    id          = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    url         = TextField(column_name='url', verbose_name='링크')
    description = TextField(column_name='description', verbose_name='설명', null=True, )
    is_top      = BooleanField(column_name='isTop', verbose_name='대표 비디오', default=False)
    news        = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News)

class Reporter(NewsDB):
    id        = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    name      = CharField(column_name='name', verbose_name='기자 이름', max_length=2048,)
    publisher = ForeignKeyField(column_name='publisher', verbose_name='신문사', model=Publisher)

class RelNewsReporter(NewsDB):
    id       = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    news     = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News)
    reporter = ForeignKeyField(column_name='reporter', verbose_name='기자', model=Reporter)

class Category(NewsDB):
    name = CharField(column_name='name', verbose_name='카테고리 이름', max_length=256, primary_key=True, )

class RelNewsCategory(NewsDB):
    id       = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    news     = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News)
    category = ForeignKeyField(column_name='category', verbose_name='카테고리', model=Category)

class Keyword(NewsDB):
    id   = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    name = CharField(column_name='name', verbose_name='키워드 이름', max_length=256)

class RelNewsKeyword(NewsDB):
    id      = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    news    = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News)
    keyword = ForeignKeyField(column_name='keyword', verbose_name='키워드', model=Keyword)

class GptResult(NewsDB):
    id       = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    provider = CharField(column_name="provider", verbose_name="제공자", max_length=256, )
    news     = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News, null=True, index=True)
    usage    = FloatField(column_name='usage', verbose_name='사용량(달러)', null=True)
    data     = JSONField()

class TrendMArticle(NewsDB):
    id       = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    template = CharField(column_name="template", verbose_name="템플릿", max_length=256, )
    news     = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News, index=True)
    image    = ForeignKeyField(column_name='image', verbose_name='이미지(TOP)', model=Image, null=True)
    
    data          = JSONField()
    published     = BooleanField(column_name='published', verbose_name='배포여부', default=False)
    published_url = TextField(column_name='publishedUrl', verbose_name='배포링크', null=True, )

class Embedding(NewsDB):
    id      = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    vector  = JSONField()
    model   = CharField(column_name='model', verbose_name='임베딩 모델', max_length=32)
    input   = TextField(column_name='input', verbose_name='입력값', null=True) # 어떤 데이터를 임베딩 한 건지

class Log(NewsDB):
    id       = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
    level    = CharField(column_name='level', verbose_name='레벨', max_length=16)
    name     = CharField(column_name='name', verbose_name='이름', max_length=256, null=True)
    message  = TextField(column_name='message', verbose_name='메세지', null=True)
    data     = JSONField(column_name="data", verbose_name="로그데이터")
    datetime = DateTimeField(column_name='datetime', verbose_name='시간', formats='%Y-%m-%d %H:%M:%S')


# Depreciate
# class TrendMSuitable(NewsDB):
#     id       = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
#     provider = CharField(column_name="provider", verbose_name="제공자", max_length=256, )
#     news     = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News)

#     suitable = BooleanField(column_name='suitable', verbose_name='적합여부', default=False)
#     reason = TextField(column_name="reason", verbose_name="적합이유", null=True,)

# class TrendMImpact(NewsDB):
#     id       = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
#     provider = CharField(column_name="provider", verbose_name="제공자", max_length=256, )
#     news     = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News)

#     summary   = TextField(column_name="summary", verbose_name="요약 내용(ENG)")
#     valueable = BooleanField(column_name='valueable', verbose_name='배포여부', default=False)
#     impact    = FloatField(column_name='impact', verbose_name='영향력')
#     usage     = DoubleField(column_name='usage', verbose_name='과금액')

# class TrendMSummary(NewsDB): 
#     id       = BigAutoField(column_name='id', verbose_name='기본키', primary_key=True)
#     provider = CharField(column_name="provider", verbose_name="제공자", max_length=256, )
#     news     = ForeignKeyField(column_name='news', verbose_name='뉴스', model=News)
#     image    = ForeignKeyField(column_name='image', verbose_name='이미지(TOP)', model=Image, null=True)
    
#     title   = CharField(column_name='title', verbose_name='제목', max_length=256)
#     summary = TextField(column_name="summary", verbose_name="요약 내용(KOR)")

#     trend   = CharField(column_name="trend", verbose_name="트렌드 패턴", max_length=64, )
#     issue   = CharField(column_name="issue", verbose_name="이슈", max_length=64, )
#     section = CharField(column_name="section", verbose_name="섹션", max_length=64, )
#     insight = TextField(column_name="insight", verbose_name="요약 내용")
#     usage   = DoubleField(column_name='usage', verbose_name='과금액')

#     keywords  = JSONField()
#     classifiy = JSONField()
#     published = BooleanField(column_name='published', verbose_name='배포여부', default=False)
#     published_url = TextField(column_name='publishedUrl', verbose_name='배포링크', null=True, )