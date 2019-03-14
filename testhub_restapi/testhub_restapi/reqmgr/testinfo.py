import logging as log_root
import json

from testhub_restapi.common import constants
from testhub_restapi.common import exception
from testhub_restapi.reqmgr.common import EventHandler
from testhub_restapi import objects

LOG = log_root.getLogger(__name__)


class TestInfoEventFactory:

    __subjects = {constants.TEST_INFO_SUBJECT_UI_CONFIG: "UiConfigJobHandler",
                  constants.TEST_INFO_SUBJECT_POD_INVENTORY: "PodInventoryEventHandler"}

    @staticmethod
    def factory(subject):
        LOG.info("TestInfoEventFactory: factory for subject: {0}".format(subject))
        if subject not in TestInfoEventFactory.__subjects.keys():
            raise exception.TestInfoEventNotFound()

        LOG.info("Creating object for class: {0}".format(TestInfoEventFactory.__subjects[subject]))
        cls = globals()[TestInfoEventFactory.__subjects[subject]]
        instance = cls()
        LOG.info("Obj: {0} type {1} created".format(instance, TestInfoEventFactory.__subjects[subject] ))
        return instance


class TestInfoJobHandler(EventHandler):

    def __init__(self):
        self.info_request = None
        LOG.info("TestInfoJobHandler: ctor")

    @property
    def info_request(self):
        return self.info_request

    @info_request.setter
    def info_request(self, ir):
        self.info_request = ir

    def acquire(self, info_request):
        LOG.info("TestInfoJobHandler: acquire")
        self.info_request = info_request

    def _update_data(self, uuid, update):
        LOG.info("TestInfo _update_data for UUID {0}".format(uuid))
        objects.TestInfo.save(uuid, update)


class UiConfigJobHandler(TestInfoJobHandler):

    def __init__(self):
        self.oid = str(self).split("0x")[-1]
        LOG.debug("UiConfigJobHandler: ctor: {0}".format(self.oid))

    def acquire(self, info_request):
        self.info_request = info_request
        LOG.info("UiConfigJobHandler{0}: acquire: info_request: {0}".format(self.oid, self.info_request))
        updated = {"status": constants.TEST_INFO_COMPLETE,
                   "testinfo_result": json.dumps({'subject': 'ui_config',
                                                  'result': {"Kibana-Url": "url",
                                                             "RestAPI-Username": "user",
                                                             "RestAPI-Password": "pw1",
                                                             "RestDB-Password": "pw2",
                                                             "RestAPI-Url": "url",
                                                             "BuildNodeIP": "192.168.1.1"}})}
        self._update_data(info_request.uuid, updated)


class PodInventoryEventHandler(TestInfoJobHandler):

    def __init__(self):
        TestInfoJobHandler.__init__(self)

    def acuire(self, info_request):
        self.info_request = info_request
        LOG.info("PodInventoryEventHandler: acquire: info_request: {0}".format(self.info_request))


