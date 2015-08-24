# -*- coding: utf-8 -*-

import json

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

from resources.functions.json import get_by_json_path

class ConfigHandler:

    @property
    def json_pretty_printing(self): return json.dumps(self._config_object, sort_keys = True, indent = 4, separators = (',', ': '))

    def __init__(self):
        self.load_config_from_configfile(DOORPI.arguments.config_file)
        logger.debug("config_object: %s", self.get_modul_config('resources.interface_handler'))
        logger.debug("config_object: %s", self.get_modul_config('resources.event_handler'))

    def start(self):
        logger.debug("start ConfigHandler with configfile %s", DOORPI.arguments.config_file)
        return self

    def load_config_from_configfile(self, config_file = None):
        with open(DOORPI.parse_string(config_file)) as data_file:
            self._config_object = json.load(data_file)
        return True

    def get_modul_config(self, modul_name, config_object = None):
        if not self._config_object: return {}
        if not config_object: config_object = self._config_object

        try:
            modul_array = modul_name.split('.')
            if len(modul_array) == 1:
                logger.debug("search for %s return", modul_array[0])
                return config_object[modul_array[0]]
            else:
                logger.debug("search for %s recursive", modul_array[0])
                return self.get_modul_config(modul_array[1], config_object[modul_array[0]])
        except KeyError:
            return {}
