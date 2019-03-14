import json
import logging as log_root
import threading
import time

from testhub_restapi.common import constants
from testhub_restapi.common import exception
from testhub_restapi.reqmgr.testinfo import TestInfoEventFactory
from testhub_restapi.reqmgr.common import Listener
from testhub_restapi import objects

LOG = log_root.getLogger(__name__)


class TestInfo(threading.Thread, Listener):

    def __init__(self):
        threading.Thread.__init__(self)
        self.worker = None
        self.q = None

    def _update_data(self, uuid, update):
        LOG.info("TestInfo _update_data for UUID {0}".format(uuid))
        objects.TestInfo.save(uuid, update)

    def _do_testinfo(self, testinfo_data):
        LOG.info("TestInfo do_testinfo, data: {0}".format(testinfo_data))
        update = {"status": constants.TEST_INFO_RUNNING}
        self._update_data(testinfo_data.uuid, update)
        try:
            LOG.debug('Starting testinfo for %s : ' % str(testinfo_data.uuid))
            handler = TestInfoEventFactory.factory(testinfo_data.subject)
            LOG.debug("Handler created: {0}".format(handler))
            LOG.debug("Acquiring test info")
            handler.acquire(testinfo_data)
            LOG.debug("Test info acquired")
        except Exception as e:
            LOG.error("Exception during Request handler dispatch: {0}".format(e))

    def run(self):
        while(True):
            time.sleep(5)
            testinfo_list = objects.TestInfo.list()
            for item in testinfo_list:
                if item.status == constants.TEST_INFO_PENDING:
                    try:
                        LOG.debug("Performing TestInfo operation for %s" %
                                  str(item.subject))
                        objects.TestInfo.get_by_uuid(item.uuid)
                        self._do_testinfo(item)
                    except Exception:
                        LOG.error('Fatal Exception', exc_info=True)
