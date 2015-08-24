# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

from resources.event_handler.docs import DOCUMENTATION as EVENT_HANDLER_DOCUMENTATION

class EventHandler:

    def __init__(self):
        DOORPI.register_module(__name__, self.start, self.stop, False)

    def start(self):
        logger.debug("start EventHandler")
        self._conf = DOORPI.config.get_modul_config(__name__, EVENT_HANDLER_DOCUMENTATION)

    def stop(self):
        pass
