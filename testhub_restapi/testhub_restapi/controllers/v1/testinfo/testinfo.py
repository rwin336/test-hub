import json
import re
import uuid

from testhub_restapi.common import constants
from testhub_restapi.common import exception
from testhub_restapi.common import utils
from testhub_restapi.controllers import base
from testhub_restapi.controllers.v1 import collection
from testhub_restapi.controllers.v1 import types
from testhub_restapi import objects
import pecan.rest
import pecan
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan
import logging 

LOG = logging.getLogger(name=__name__)


###############################################################################
# TestInfo
#
# TestInfo request
#
#  {
#   'testinfo_request': {
#              'uuid': '',
#              'subject': ''
#              }
#  }
#
#  Example:
#  {
#   'testinfo_request': {
#               'uuid': '',
#               'subject': 'ui_config'
#              }
#  }
#
#
# TestInfo Response:
#
#
#


class TestInfo(base.APIBase):

    subject = wtypes.text
    testinfo_request = types.testinfodata
    testinfo_result = wtypes.text
    status = wtypes.text

    def __init__(self, **kwargs):
        super(TestInfo, self).__init__()
        self.fields = []

        for field in ['uuid', 'subject', 'status', 'testinfo_request',
                      'testinfo_result', 'created_at', 'updated_at']:
            if not hasattr(self, field):
                continue
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @staticmethod
    def _convert_with_links(test, url, expand=True):
        return test

    @classmethod
    def convert_with_links(cls, test, expand=True):

        subject = TestInfo(**test.as_dict())
        return cls._convert_with_links(subject, pecan.request.host_url, expand)


class TestInfoDeleteResponse(base.APIBase):

    uuid = wtypes.text
    status = wtypes.text
    error = wtypes.text
    message = wtypes.text

    def __init__(self, **kwargs):
        super(TestInfoDeleteResponse, self).__init__()

        self.fields = []

        for field in ['status', 'error']:
            if not hasattr(self, field):
                continue
            self.fields.append(field)
            setattr(self, field, kwargs.get(field, wtypes.Unset))

    @staticmethod
    def _convert_with_links(test, url, expand=True):
        return test

    @classmethod
    def convert_with_links(cls, rpc_test, expand=True):

        test = TestInfoDeleteResponse(**rpc_test.as_dict())
        return cls._convert_with_links(test, pecan.request.host_url, expand)


class TestInfoCollection(collection.Collection):

    testinfo_list = [TestInfo]

    def __init__(self, **kwargs):
        self._type = 'setupdatas'

    @staticmethod
    def convert_with_links(testinfo_objs):
        LOG.debug("TestInfoCollection: convert_with_links")
        collec = TestInfoCollection()
        collec.testinfo_list = [TestInfo.convert_with_links(p)
                        for p in testinfo_objs]
        LOG.debug("collec = {0}".format(collec))
        return collec


class TestInfoController(pecan.rest.RestController):

    _custom_actions = {
        'show': ['GET'],
        'list': ['GET'],
        'create': ['POST'],
        'delete': ['DELETE'],
    }

    _valid_actions = ['create', 'delete', 'show', 'list']

    _valid_subjects = accepted = ['pod_inventory']


    @pecan.expose('json')
    def get_all(self):
        LOG.debug("Reached root of  testinfo get_all: Getting testinfo objs")
        testinfo_obj_list = objects.TestInfo.get_testinfo_list()
        LOG.debug("TestInfo objects obtained: len = {0}".format(len(testinfo_obj_list)))
        ti_result = {}

        for item in testinfo_obj_list:
            ti_result[item.uuid] = {
                'uuid': item.uuid,
                'status': item.status,
                'created_at': item.created_at,
                'subject': item.subject
            }
        return ti_result

    @pecan.expose('json')
    def list(self, **kwargs):
        if 'subject' not in kwargs:
            LOG.debug("Missing arguments: Expected action/test_name: Actual: {0}".format(kwargs))
            pecan.abort(404, detail="Error details: Missing arguments: subject")

        if kwargs['subject'] not in self._valid_subjects:
            LOG.debug("Subject {0} not in list of valid Info Subjects".format(kwargs['subject']))
            pecan.abort(404, detail="Subject name {0} not in list of valid info subjects".format(kwargs['subject']))

        LOG.debug("Reached root of get list: args: test_name={0}".format(kwargs['subject']))
        ti_result = {}
        return ti_result

    @pecan.expose('json')
    def show(self, **kwargs):
        LOG.debug("Reached testinfo show with %s", kwargs)
        if 'uuid' not in kwargs:
            LOG.debug("Missing arguments: Expected uuid: Actual: {0}".format(kwargs))
            pecan.abort(404, detail="Error details: Missing arguments")

        try:
            testinfo_obj = objects.TestInfo.get_by_uuid(str(kwargs['uuid']))
        except exception.TestInfoDataNotFound as e:
            LOG.debug("TestInfoDataNotFound not found for uuid {0}".format(kwargs['uuid']))
            pecan.abort(404, detail="TestInfoDataNotFound not found for uuid {0}".format(kwargs['uuid']))

        return testinfo_obj.as_dict()

    def _run_testinfo(self, testinfo_request):
        # Delete an Old TestInfo Test Entry if exists
        try:
            LOG.debug("Checking previous test run for {0} if exists".format(testinfo_request))
            testinfo_test_done_states = [constants.TEST_INFO_COMPLETE, constants.TEST_INFO_FAILED]
            testinfo = objects.TestInfo.get_by_status(constants.TEST_INFO_RUNNING)
            if testinfo:
                LOG.debug("Found previous testinfo run: state: {0}".format(testinfo.status))
                if testinfo.status not in testinfo_test_done_states:
                    LOG.debug("Test {0} still in-progress".format(testinfo_request['subject']))
                    pecan.abort(403, detail="Test name {0} still in-progress, please wait for it to complete".format(
                        testinfo_request['subject']))
            else:
                LOG.debug("No previous testinfo run found")
        except exception.TestInfoDataNotFound:
            LOG.debug("No currently running testinfo request detected ")

        testinfo_data = {}
        ti_uuid = str(uuid.uuid4())
        testinfo_request['uuid'] = ti_uuid
        testinfo_data['uuid'] = ti_uuid
        testinfo_data['subject'] = testinfo_request['subject']
        testinfo_data['status'] = constants.TEST_INFO_PENDING
        #testinfo_data['testinfo_request'] = json.dumps(testinfo_request)
        testinfo_data['testinfo_request'] = ""
        testinfo_data['testinfo_result'] = ""
        LOG.debug("Creating testinfo object: {0}".format(testinfo_data))
        created = objects.TestInfo.create(testinfo_data)

        try:
            objects.TestInfo.save(ti_uuid, testinfo_data)
        except Exception as e:
            LOG.debug("Exception saving/creating testinfo_data: {0}".format(e))
        LOG.debug("Create complete")
        return created

    @wsme_pecan.wsexpose(TestInfo, body=TestInfo, status_code=201)
    def create(self, testinfo):
        LOG.debug("Reached test info create: args = {0}".format(TestInfo))

        testinfo_request_str = json.dumps(testinfo.testinfo_request)
        testinfo_request = json.loads(testinfo_request_str)
        LOG.debug("TestInfo request: {0}".format(testinfo_request))
        return self._run_testinfo(testinfo_request)

    @pecan.expose('json')
    def delete(self, **kwargs):
        LOG.debug("Reached testinfo delete with %s", kwargs)

        if 'uuid' not in kwargs:
            LOG.debug("Missing arguments: Expected uuid: Actual: {0}".format(kwargs))
            pecan.abort(404, detail="Error details: Missing arguments")

        LOG.debug("TestInfo delete request UUID: {0}".format(kwargs['uuid']))
        try:
            LOG.debug("TestInfo: Delete: getting uuid from database")
            testinfo = objects.TestInfo.get_by_uuid(kwargs['uuid'])
            LOG.debug("TestInfo: Delete: Received object from database: {0}".format(testinfo))
            if testinfo.status == constants.TEST_INFO_RUNNING:
                status = 'failed'
                error = 'UUID {0} still running'.format(kwargs['uuid'])
                msg = 'UUID {0} not deleted from database'.format(kwargs['uuid'], status)
                pecan.abort(409, detail=error)
            else:
                LOG.debug("Performing delete")
                testinfo.delete()
                status = 'deleted'
                error = 'None'
                msg = 'UUID {0} deleted from database'.format(kwargs['uuid'])
                LOG.debug("Delete complete: {0}".format(kwargs['uuid']))
        except exception.TestInfoDataNotFound as e:
            LOG.debug("TestInfoDataNotFound not found for uuid {0}".format(kwargs['uuid']))
            pecan.abort(404, detail="Error details: " + str(e))

        tidr = {'uuid': kwargs['uuid'],
                'status': status,
                'error': error,
                'message': msg}
        return tidr
