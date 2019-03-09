from testhub_restapi.controllers import base
import pecan
from wsme import types as wtypes


def build_url(resource, resource_args, bookmark=False, base_url=None):
    if base_url is None:
        base_url = pecan.request.host_url

    template = '%(url)s/%(res)s' if bookmark else '%(url)s/v1/%(res)s'
    template += '%(args)s' if resource_args.startswith('?') else '/%(args)s'
    return template % {'url': base_url, 'res': resource, 'args': resource_args}


class Link(base.APIBase):
    href = wtypes.text
    rel = wtypes.text
    type = wtypes.text

    @staticmethod
    def make_link(rel_name, url, resource, resource_args,
                  bookmark=False, type=wtypes.Unset):
        href = build_url(resource, resource_args,
                         bookmark=bookmark, base_url=url)
        return Link(href=href, rel=rel_name, type=type)

