# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

class InterfaceHandler:

    def __init__(self):
        pass

    def start(self):
        logger.debug("start InterfaceHandler")
