import abc

from oslo_config import cfg
from oslo_db import api as db_api
import six


_BACKEND_MAPPING = {'sqlalchemy': 'testhub_restapi.db.sqlalchemy.api'}
IMPL = db_api.DBAPI.from_config(cfg.CONF, backend_mapping=_BACKEND_MAPPING,
                                lazy=True)


def get_instance():
    return IMPL


@six.add_metaclass(abc.ABCMeta)
class Connection(object):

    @abc.abstractmethod
    def __init__(self):
        """Constructor."""

