from peewee import *
from utils import Env
class NewsDB(Model):
    class Meta:
        database = PostgresqlDatabase(
            Env.get('POSTGRESQL_DB'),
            user     = Env.get('POSTGRESQL_USER'),
            password = Env.get('POSTGRESQL_PASSWORD'),
            host     = Env.get('POSTGRESQL_HOST'),
            port     = Env.get('POSTGRESQL_PORT'))