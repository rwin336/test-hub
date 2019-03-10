from testhub_restapi.controllers import base
from testhub_restapi.controllers import link
from testhub_restapi.controllers.v1 import v1

from pecan import expose, redirect
from webob.exc import status_map
import pecan
from wsme import types as wtypes
import wsmeext.pecan as wsme_pecan


class Version(base.APIBase):
    id = wtypes.text
    links = [link.Link]

    @staticmethod
    def convert(id):
        version = Version()
        version.id = id
        version.links = [link.Link.make_link('self', pecan.request.host_url,
                                             id, '', bookmark=True)]
        return version

class Root(base.APIBase):

    name = wtypes.text

    description = wtypes.text

    versions = [Version]

    default_version = Version

    @staticmethod
    def convert():
        root = Root()
        root.name = "Test Hub Rest API"
        root.description = (
            "Test Hub Rest API is used to "
            "invoke testing operations from API.")
        root.versions = [Version.convert('v1')]
        root.default_version = Version.convert('v1')
        return root



class RootController(pecan.rest.RestController):

    _versions = ['v1']

    _default_version = 'v1'

    v1 = v1.Controller()

    @wsme_pecan.wsexpose(Root)
    def get(self):
        return Root.convert()

    @pecan.expose()
    def _route(self, args):

        if args[0] and args[0] not in self._versions:
            args = [self._default_version] + args
        return super(RootController, self)._route(args)

