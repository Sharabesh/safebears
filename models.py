import os 
import peewee
import playhouse
import psycopg2
from peewee import CharField, DateTimeField, IntegerField
from playhouse import signals
from playhouse.postgres_ext import *


url = urlparse(os.environ["DATABASE_ENTRY"])

config = dict(
    database=url.path[1:],
    user=url.username,
    password=url.password,
    host=url.hostname,
    port=url.port,
    sslmode='require'
)

conn = PostgresqlExtDatabase(
    autocommit=True,
    autorollback=True,
    register_hstore=False,
    **config
)


class BaseModel(signals.Model):

	class Meta:
		database = conn 


class Test(BaseModel):


	class Meta:
		db_table = "Test"