from testhub_restapi.common import exception
from testhub_restapi.db import api
from testhub_restapi.db.sqlalchemy import models
from oslo_config import cfg
from oslo_db import exception as db_exc
from oslo_db.sqlalchemy import session as db_session
import sqlalchemy.orm.exc

CONF = cfg.CONF

_FACADE = None


def _create_facade_lazily():
    global _FACADE
    if _FACADE is None:
        _FACADE = db_session.EngineFacade.from_config(CONF)
    return _FACADE


def get_engine():
    facade = _create_facade_lazily()
    return facade.get_engine()


def get_session(**kwargs):
    facade = _create_facade_lazily()
    return facade.get_session(**kwargs)


def get_backend():
    return Connection()


def model_query(model, *args, **kwargs):

    session = kwargs.get('session') or get_session()
    query = session.query(model, *args)
    return query


class Connection(api.Connection):

    def __init__(self):
        pass

    def get_testinfo_list(self):
        query = model_query(models.testinfo)
        return query.all()

    def get_testinfo_by_status(self, status):
        query = model_query(models.testinfo)
        query = query.filter_by(status=status)
        try:
            return query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.TestInfoDataNotFound()

    def get_testinfo_by_uuid(self, uuid):
        query = model_query(models.testinfo)
        query = query.filter_by(uuid=uuid)
        try:
            return query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.TestInfoDataNotFound()

    def create_testinfo(self, values):
        testinfo = models.testinfo()
        testinfo.update(values)
        try:
            testinfo.save()
        except db_exc.DBDuplicateEntry:
            raise exception.TestInfoNotUnique()
        return testinfo

    def get_testinfo_by_subject(self, subject):
        query = model_query(models.testinfo)
        query = query.filter_by(subject=subject)
        try:
            return query.all()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.TestInfoDataNotFound()

    def delete_testinfo(self, uuid):
        query = model_query(models.testinfo)
        query = query.filter_by(uuid=uuid)
        try:
            setupdata_ref = query.one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.TestInfoDataNotFound()
        query.delete()
        return setupdata_ref

    def update_testinfo(self, uuid, values):
        query = model_query(models.testinfo)
        query = query.filter_by(uuid=uuid)
        try:
            ref = query.with_lockmode('update').one()
        except sqlalchemy.orm.exc.NoResultFound:
            raise exception.TestInfoDataNotFound()
        query.update(values)
        return ref

