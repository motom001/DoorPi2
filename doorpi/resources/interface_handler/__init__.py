# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

import importlib

class MissingInterfaceTypException(Exception): pass
class InterfaceNameAlreadyExistsException(Exception): pass

class InterfaceHandler:

    _interfaces = dict()

    def __init__(self):
        pass

    def start(self):
        logger.debug("start InterfaceHandler")
        for interface_name in DOORPI.config('/interfaces', default = [], function = 'keys'):
            self.load_interface('/interfaces/', interface_name)
        logger.debug('loaded %s interfaces', len(self._interfaces))

    def stop(self):
        logger.debug("stop InterfaceHandler")

    def get_interface_by_name(self, interface_name):
        if interface_name in self._interfaces:
            return self._interfaces[interface_name]
        else:
            return None

    def load_interface(self, config_path, interface_name):
        try:
            module_type = DOORPI.config(config_path + interface_name + '/type', None)
            if not module_type: raise MissingInterfaceTypException()
            interface_object = importlib.import_module(DOORPI.CONST.INTERFACES_BASE_IMPORT_PATH + module_type).__interface__(
                name = interface_name,
                config_path = config_path + interface_name
            )
            if interface_name in self._interfaces:
                raise InterfaceNameAlreadyExistsException(interface_name)
            else:
                self._interfaces[interface_name] = interface_object.start()
        except Exception as exp:
            logger.exception('failed to load interface with error %s', exp)

    __call__ = get_interface_by_name
