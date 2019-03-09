import logging

import six

LOG = logging.getLogger(__name__)


class RestApiException(Exception):
    message = "An unknown exception occurred."
    code = 500

    def __init__(self, message=None, **kwargs):
        self.kwargs = kwargs
        if 'code' not in self.kwargs:
            try:
                self.kwargs['code'] = self.code
            except AttributeError:
                pass
        if message:
            self.message = message

        try:
            self.message = self.message % kwargs
        except Exception as e:
            LOG.exception('Exception in string format operation')
            for name, value in kwargs.iteritems():
                LOG.error(("%(name)s: %(value)s") %
                          {'name': name, 'value': value})
            raise e
        super(RestApiException, self).__init__(self.message)

    def __str__(self):
        if six.PY3:
            return self.message
        return self.message.encode('utf-8')

    def __unicode__(self):
        return self.message

    def format_message(self):
        if self.__class__.__name__.endswith('_Remote'):
            return self.args[0]
        else:
            return six.text_type(self)

