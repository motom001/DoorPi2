# -*- coding: utf-8 -*-

__all__ = ["DoorPi"]

from resources.logging import DoorPiMemoryLog, init_own_logger
logger = init_own_logger(__name__)

import main

class DoorPi(object):
    _instance = None
    _logger = None
    _argumentes = None

    @property
    def logger(self): return self._logger

    def __init__(self,):
        pass

    def restart(self):
        logger.debug('restart')
        self.stop()
        self.__init__()
        self.start()

    def prepare(self, **arguments):
        self._argumentes = arguments
        self._logger = DoorPiMemoryLog()

    def start(self):
        logger.debug('start')

    def stop(self):
        logger.debug('stop')
        if self.logger: self.logger.close()

    def test(self):
        logger.debug('test')

    run = start
    destroy = stop
    #__del__ = stop
