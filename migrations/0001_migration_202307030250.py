# auto-generated snapshot
from peewee import *
import datetime
import peewee


snapshot = Snapshot()


@snapshot.append
class Category(peewee.Model):
    name = CharField(max_length=256, primary_key=True)
    class Meta:
        table_name = "category"


@snapshot.append
class Publisher(peewee.Model):
    id = BigAutoField(primary_key=True)
    name = CharField(max_length=256)
    url = TextField()
    is_crawling_possible = BooleanField(column_name='isCrawlingPossible', default=True)
    class Meta:
        table_name = "publisher"


@snapshot.append
class News(peewee.Model):
    id = BigAutoField(primary_key=True)
    url = TextField()
    url_origin = TextField(column_name='urlOrigin', null=True)
    title = CharField(max_length=256)
    description = TextField(null=True)
    publisher = snapshot.ForeignKeyField(column_name='publisher', index=True, model='publisher')
    article = TextField(null=True)
    country = FixedCharField(max_length=2)
    language = FixedCharField(max_length=2)
    date_pub = DateTimeField(column_name='datePub', formats='%Y-%m-%d %H:%M:%S')
    date_collect = DateTimeField(column_name='dateCollect', formats='%Y-%m-%d %H:%M:%S')
    class Meta:
        table_name = "news"


@snapshot.append
class Image(peewee.Model):
    id = BigAutoField(primary_key=True)
    url = TextField()
    description = TextField(null=True)
    is_top = BooleanField(column_name='isTop', default=False)
    news = snapshot.ForeignKeyField(column_name='news', index=True, model='news')
    class Meta:
        table_name = "image"


@snapshot.append
class Keyword(peewee.Model):
    id = BigAutoField(primary_key=True)
    name = CharField(max_length=256)
    class Meta:
        table_name = "keyword"


@snapshot.append
class RelNewsCategory(peewee.Model):
    id = BigAutoField(primary_key=True)
    news = snapshot.ForeignKeyField(column_name='news', index=True, model='news')
    category = snapshot.ForeignKeyField(column_name='category', index=True, model='category')
    class Meta:
        table_name = "relnewscategory"


@snapshot.append
class RelNewsKeyword(peewee.Model):
    id = BigAutoField(primary_key=True)
    news = snapshot.ForeignKeyField(column_name='news', index=True, model='news')
    keyword = snapshot.ForeignKeyField(column_name='keyword', index=True, model='keyword')
    class Meta:
        table_name = "relnewskeyword"


@snapshot.append
class Reporter(peewee.Model):
    id = BigAutoField(primary_key=True)
    name = CharField(max_length=2048)
    publisher = snapshot.ForeignKeyField(column_name='publisher', index=True, model='publisher')
    class Meta:
        table_name = "reporter"


@snapshot.append
class RelNewsReporter(peewee.Model):
    id = BigAutoField(primary_key=True)
    news = snapshot.ForeignKeyField(column_name='news', index=True, model='news')
    reporter = snapshot.ForeignKeyField(column_name='reporter', index=True, model='reporter')
    class Meta:
        table_name = "relnewsreporter"


@snapshot.append
class Summary(peewee.Model):
    id = BigAutoField(primary_key=True)
    title = CharField(max_length=256, null=True)
    text = TextField()
    provider = CharField(max_length=256)
    news = snapshot.ForeignKeyField(column_name='news', index=True, model='news')
    class Meta:
        table_name = "summary"


@snapshot.append
class Video(peewee.Model):
    id = BigAutoField(primary_key=True)
    url = TextField()
    description = TextField(null=True)
    is_top = BooleanField(column_name='isTop', default=False)
    news = snapshot.ForeignKeyField(column_name='news', index=True, model='news')
    class Meta:
        table_name = "video"


