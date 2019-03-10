from testhub_restapi.common import constants
import testhub_restapi.db.api as db_api
from testhub_restapi.objects.utils import add_utc_timezone


class TestInfo(object):

    def __init__(self, **kwargs):
        self._changed_fields = set()
        for key in kwargs.keys():
            setattr(self, key, kwargs[key])

    def __getitem__(self, key):
        return getattr(self, key)

    def __setitem__(self, key, value):
        setattr(self, key, value)

    def as_dict(self):
        return dict((k, getattr(self, k))
                    for k in self.fields
                    if hasattr(self, k))

    @classmethod
    def obj_name(cls):
        return cls.__name__

    dbapi = db_api.get_instance()

    fields = {
        'created_at': "",
        'updated_at': "",
        'uuid': "",
        'action': "",
        'subject': "",
        'status': "",
        'testinfo_result': "",
        'testinfo_request': ""
    }

    @staticmethod
    def _from_db_object(testinfo, db):
        """Converts a database entity to a formal object."""
        for field in testinfo.fields:
            testinfo[field] = db[field]

        return testinfo

    @staticmethod
    def _from_dict_object(testinfo, mydict):
        for field in testinfo.fields:
            testinfo[field] = mydict[field]
            if testinfo['created_at']:
                testinfo['created_at'] = add_utc_timezone(testinfo['created_at'])
            if testinfo['updated_at']:
                testinfo['updated_at'] = add_utc_timezone(testinfo['updated_at'])

        return testinfo

    @staticmethod
    def _from_db_object_list(db_objects, cls):
        """Converts a list of db entities to a list of formal objects."""
        return [TestInfo._from_db_object(cls(), obj)
                for obj in db_objects]

    @classmethod
    def get_testinfo_list(cls):
        db = cls.dbapi.get_testinfo_list()
        testinfo = TestInfo._from_db_object_list(db, cls)
        return testinfo

    @classmethod
    def get_by_subject(cls, subject):
        db = cls.dbapi.get_testinfo_by_subject(subject)
        testinfo = TestInfo._from_db_object_list(db, cls)
        return testinfo

    @classmethod
    def get_by_status(cls, status):
        db = cls.dbapi.get_testinfo_by_status(status=status)
        testinfo = TestInfo._from_db_object(cls(), db)
        return testinfo

    @classmethod
    def get_by_uuid(cls, uuid):
        db = cls.dbapi.get_testinfo_by_uuid(uuid)
        testinfo = TestInfo._from_db_object(cls(), db)
        return testinfo

    @classmethod
    def list(cls):
        db = cls.dbapi.get_testinfo_list()
        return TestInfo._from_db_object_list(db, cls)

    @classmethod
    def create(cls, values):

        db = cls.dbapi.create_testinfo(values)
        testinfo = TestInfo._from_db_object(cls(), db)
        return testinfo

    @classmethod
    def save(cls, uuid, values):

        db = cls.dbapi.update_testinfo(uuid, values)
        testinfo = TestInfo._from_db_object(cls(), db)
        return testinfo

    def delete(self):
        self.dbapi.delete_testinfo(self.uuid)

    @classmethod
    def cleanup(cls):
        testinfo_list = cls.list()
        if testinfo_list:
            for testinfo in testinfo_list:
                update = {}
                if testinfo.status == constants.TEST_INFO_RUNNING:
                    newupdate = {'status': constants.TEST_INFO_FAILED}
                    update.update(newupdate)
            if update:
                cls.save(testinfo.subject, **update)

