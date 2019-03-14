import threading
import logging as log_root
from testhub_restapi import objects
from testhub_restapi.common import exception

LOG = log_root.getLogger(__name__)


class Listener:

    def __init__(self):
        self.__events = []
        self.oid = str(self).split("0x")[-1]

    def notify(self, uuid):
        if uuid in self.__events:
            self.__events.remove(uuid)

    def watchdog(self):
        pass

    @property
    def events(self):
        return self.__events

    @events.setter
    def events(self, events):
        self.__events = events

    @property
    def oid(self):
        return self.oid

    @oid.setter
    def oid(self, oid):
        self.oid = oid


class EventHandler:

    def __init__(self):
        self.__listeners = []
        self.oid = str(self).split("0x")[-1]

    def register(self, listener):
        LOG.info("EventHandler {0}: register: listener: {1}".format(self.oid, listener.oid))
        self.__listeners.append(listener)

    def notify(self):
        LOG.info("EventHandler {0}: notify: listeners")
        for listener in self.listeners:
            LOG.info("EventHandler {0}: notify: listener {1}".format(self.oid, listener.oid))
            listener.notify()

    def acquire(self, item):
        pass

    @property
    def listeners(self):
        return self.__listeners

    def run(self):
        pass
