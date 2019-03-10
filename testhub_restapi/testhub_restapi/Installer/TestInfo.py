import json
import logging as log_root
import threading
import time

from testhub.common import constants
from testhub.common import utils
from testhub import objects

LOG = log_root.getLogger(__name__)

class TestInfo(threading.Thread):

    def __init__(self):
        threading.Thread.__init__(self)
        self.worker = None
        self.q = None

    def _update_data(self, uuid, update):
	LOG.info("TestInfo _update_data for UUID {0}".format(uuid))
        objects.TestInfo.save(uuid, update)


    def _do_testinfo(self, testinfo_data):
	LOG.info("TestInfo do_testinfo, data: {0}".format(data))
        testinfo_status = constants.TEST_INFO_FAILED

        return testinfo_status

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

