import logging
import wsgiref.simple_server as wsgisrv

logger = logging.getLogger(__name__)


class LogWSGIRequestHandler(wsgisrv.WSGIRequestHandler, object):

    def __init__(self, *args, **kwargs):
        self.path = ''
        super(LogWSGIRequestHandler, self).__init__(*args, **kwargs)

    def log_message(self, format, *args):

        code = args[1][0]
        levels = {
            '4': 'warning',
            '5': 'error'
        }

        log_handler = getattr(logger, levels.get(code, 'info'))
        log_handler(format % args)

