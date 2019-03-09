import pecan
import logging
import signal
import sys
import traceback

from testhub_restapi.app import config as restapi_config
from testhub_restapi import model
from testhub_restapi import objects
from oslo_config import cfg
from pecan.hooks import PecanHook
from pecan import make_app
from testhub_restapi import model


LOG = logging.getLogger(__name__)

bind_opts = [
    cfg.StrOpt('host', default='127.0.0.1',
               help=('Address to bind the server.  Useful when '
                     'selecting a particular network interface.')),
    cfg.IntOpt('port', default='8554',
               help=('The port on which the server will listen.')),
]
CONF = cfg.CONF
CONF.register_opts(bind_opts)

def get_pecan_config():
    filename = restapi_config.__file__.replace('.pyc', '.py')
    return pecan.configuration.conf_from_file(filename)

def signal_handler_traceback(signal_no, frame):
    """
    Signal Handler called in case of user fire command ""
    """
    log_msg = list()
    # Main REST API Process Traceback Logging
    log_msg.append("** Got Signal Handler {} ***".format(signal_no, frame))
    log_msg.append("** Main Process Traceback - START ***")
    for filename, lineno, name, line in traceback.extract_stack(frame):
        if not line:
            continue
        log_msg.append("{}".format(line.strip()))
    log_msg.append("** Main Process Traceback - END ***")

    # Main REST API Threads Traceback Logging
    log_msg.append("** Threads STACKTRACE - START ***")
    for threadId, stack in sys._current_frames().items():
        log_msg.append("\n# ThreadID: %s" % threadId)
        for filename, lineno, name, line in traceback.extract_stack(stack):
            log_msg.append('File: "%s", line %d, in %s' % (filename, lineno, name))
            if line:
                log_msg.append("  %s" % (line.strip()))
    log_msg.append("** Threads STACKTRACE - END ***")

    # Log Messages to Log File
    for line in log_msg:
        LOG.info(line)
    [h_weak_ref().flush() for h_weak_ref in logging._handlerList]

    # Log Messages in /root location
    with open("/root/restapi_hung_issue.txt", 'w+') as fp:
        for line in log_msg:
            fp.write("{}\n".format(line))


def cleanup():
    try:
        objects.TestInfo.cleanup()
    except Exception:
        LOG.debug("Skipping exception during cleanup")



class ErrorHook(PecanHook):

    def on_error(self, state, ex):
        if hasattr(state.controller, 'im_class') and \
                hasattr(state.controller, 'im_func'):
            LOG.error("Exception in method: {}:{} {}:{}".format(
                state.controller.im_class.__name__,
                state.controller.im_func.__name__,
                type(ex).__name__, ex.args))

    def after(self, state):
        # If Response of Method is not of Pecan Response Type then Log Error
        if not isinstance(state.response, pecan.core.Response):
            LOG.error("ERROR: API existed with: {}".format(
                state.response.status))
            return

        # Get 'json_body' of REST API Response
        if not hasattr(state.response, 'json_body') or \
                not getattr(state.response, 'json_body'):
            return

        # Get 'fault_string' of json_body from Pecan Response
        fault_string = state.response.json_body.get('faultstring', None)
        if fault_string:
            LOG.error("Exception in method: {}:{}".format(
                state.controller.im_class.__name__,
                state.controller.im_func.__name__))
            LOG.error("Fault String: {}".format(fault_string))


def setup_app(config=None):
    if not config:
        config = get_pecan_config()
    model.init_model()
    app_conf = dict(config.app)

    # Cleanup if there is any other uncleaned states
    cleanup()
    TestInfoapp = TestInfo()
    TestInfoapp.deamon = True
    TestInfoapp.start()

    pecan_app = pecan.make_app(app_conf.pop('root'),
                               logging=getattr(config, 'logging', {}),
                               hooks=[ErrorHook()],
                               **app_conf)
    # This Single is useful for the purpose of Debugging of REST API Hang Issue.
    # To get Traceback of all threads, "systemctl stop testhub-restapi"
    signal.signal(signal.SIGUSR2, signal_handler_traceback)

    return pecan_app

