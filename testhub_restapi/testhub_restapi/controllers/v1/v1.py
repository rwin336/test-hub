import os
import json

from testhub_restapi.controllers import base
from testhub_restapi.controllers import link
from testhub_restapi.controllers.v1.testinfo import testinfo
from testhub_restapi import objects

import pecan
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan

import logging

LOG = logging.getLogger(__name__)

BASE_VERSION = 1

MIN_VER_STR = '1.1'

MAX_VER_STR = '1.1'


MIN_VER = '1.1'
MAX_VER = '1.1'

version_file = "/etc/testhub-version.txt"


class VersionController(pecan.rest.RestController):

    @pecan.expose('json')
    def get_all(self):
        version_info = {}
        if os.path.isfile(version_file):
            try:
                fp = open(version_file)
                version = fp.read().strip()
                fp.close()
                version_info['version'] = version
            except Exception:
                LOG.debug("Version file not found")
        return version_info


class V1(base.APIBase):
    id = wtypes.text
    setupdata = [link.Link]
    install = [link.Link]

    @staticmethod
    def convert():
        v1 = V1()
        v1.id = "v1"
        v1.links = [link.Link.make_link('self', pecan.request.host_url,
                                        'v1', '', bookmark=True)
                    ]
        v1.setupdata = [link.Link.make_link('self', pecan.request.host_url,
                                            'setupdata', '')
                        ]
        v1.install = [link.Link.make_link('self', pecan.request.host_url,
                                          'install', '')
                      ]
        return v1


class Controller(pecan.rest.RestController):
    testinfo = testinfo.TestInfoController()

    @wsme_pecan.wsexpose(V1)
    def get(self):
        return V1.convert()

__all__ = (Controller)


