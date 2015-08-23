# -*- coding: utf-8 -*-

__all__ = ["DoorPi"]

from resources.logging import DoorPiMemoryLog, init_own_logger
logger = init_own_logger(__name__)

import time, os
import main

class DoorPi(object):
    _instance = None
    _argumentes = None
    _modules = []

    _destroy = False
    _prepared = False

    _logger = None
    _config_handler = None
    _event_handler = None
    _interface_handler = None

    stdin_path = ''
    stdout_path = ''
    stderr_path = ''
    pidfile_path =  ''
    pidfile_timeout = ''

    _start_as_daemon = True

    @property
    def logger(self): return self._logger

    def __init__(self,):
        pass

    def restart(self):
        logger.debug('restart')
        self.stop()
        self.__init__()
        self.start()

    def prepare(self, arguments):
        if arguments: self._argumentes = arguments
        if not self._logger:
            logger.debug('set new logger DoorPiMemoryLog')
            self._logger = DoorPiMemoryLog()

        # for start as daemon - if start as app it will not matter to load this vars
        self.stdin_path = main.parse_string(main.CONST.DAEMON_STDIN_PATH)
        self.stdout_path = main.parse_string(main.CONST.DAEMON_STDOUT_PATH)
        self.stderr_path = main.parse_string(main.CONST.DAEMON_STDERR_PATH)
        self.pidfile_path =  main.parse_string(main.CONST.DAEMON_PIDFILE)
        self.pidfile_timeout = main.CONST.DAEMON_PIDFILE_TIMEOUT

        self._prepared = True

    def start(self, start_as_daemon = True):
        self._start_as_daemon = start_as_daemon
        if not self._prepared: self.prepare()
        logger.debug('start')
        while True:
            #time.sleep(0.1)
            logger.debug('wait another second and DoorPiMemoryLog is %s entries long'%len(self.logger.log))
        return self

    def destroy(self):
        logger.debug('stop')
        if self.logger: self.logger.close()
        if not self._start_as_daemon: logger.info('======== DoorPi successfully shutdown ========')
        return self

    def test(self):
        logger.debug('test')

    def register_modul(self, modul_name):
        logger.debug("register modul_name")
        self._modules.append({
            'time': time.time(),
            'name': modul_name
        })
        from resources.logging import init_own_logger
        new_logger = init_own_logger(modul_name)
        new_logger.debug('load %s'%modul_name)
        return new_logger

    run = start
    stop = destroy
    #__del__ = stop
