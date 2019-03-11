from oslo_config import cfg
from oslo_db import options as db_options
from oslo_db.sqlalchemy import models
import ConfigParser
import six.moves.urllib.parse as urlparse
from sqlalchemy import Column
from sqlalchemy.ext.declarative import declarative_base
from sqlalchemy.dialects.mysql import LONGTEXT
from sqlalchemy import schema
from sqlalchemy import String

sql_opts = [
    cfg.StrOpt('mysql_engine',
               default='InnoDB',
               help='MySQL engine to use.'),
    cfg.IntOpt('max_db_entries',
               default=10,
               help=('Maximum test result entries to be persisted ')),

]

cfg.CONF.register_opts(sql_opts, 'database')


def table_args():

    if getattr(cfg.CONF.database, 'connection', None) is None:
        app_file = '/opt/testhub/testhub_restapi/app.conf'
        config = ConfigParser.RawConfigParser()
        config.read(app_file)
        connection_url = config.get('database', 'connection')
    else:
        connection_url = cfg.CONF.database.connection

    engine_name = urlparse.urlparse(connection_url).scheme
    if engine_name == 'mysql':
        return {'mysql_engine': cfg.CONF.database.mysql_engine,
                'mysql_charset': "utf8"}
    return None


class RestApiBase(models.TimestampMixin,
                  models.ModelBase):

    metadata = None

    def as_dict(self):
        d = {}
        for c in self.__table__.columns:
            d[c.name] = self[c.name]
        return d

    def save(self, session=None):
        import testhub_restapi.db.sqlalchemy.api as db_api

        if session is None:
            session = db_api.get_session()

        super(RestApiBase, self).save(session)

Base = declarative_base(cls=RestApiBase)


class testinfo(Base):
    __tablename__ = 'test_info'
    __table_args__ = (
        schema.UniqueConstraint('uuid', name='uniq_test0uuid'),
        table_args()
    )
    uuid = Column(String(64), primary_key=True)
    subject = Column(String(64))
    status = Column(String(64))
    testinfo_result = Column(LONGTEXT())
    testinfo_request = Column(LONGTEXT())


