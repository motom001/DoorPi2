# -*- coding: utf-8 -*-

import json
import importlib

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

from resources.functions.json import get_by_json_path

class ConfigHandler:

    _config_object = {}

    @property
    def json_pretty_printing(self): return json.dumps(self._config_object, sort_keys = True, indent = 4, separators = (',', ': '))

    def __init__(self):
        pass

    def start(self):
        logger.debug("start ConfigHandler with configfile %s", DOORPI.arguments.config_file)
        DOORPI.register_module(__name__, self.start, self.stop)
        self._config_object = self.load_config_from_configfile(DOORPI.arguments.config_file)
        return self

    def stop(self):
        logger.debug("stop ConfigHandler")

    def load_config_from_configfile(self, config_file = None):
        with open(DOORPI.parse_string(config_file)) as data_file:
            config_object = json.load(data_file)
        return config_object

    def get_by_path(self, json_path, default = None, config_object = None, module_name = None):
        # TODO: hole aus Docu den Parameter und nutze defaultund type für bessere Kontrolle
        # dict( json_path = 'resources/event_handler/event_log/typ', type = 'string', default = 'sqllite', mandatory = False, description = 'Typ der Event_Handler Datenbank (aktuell nur sqllite)')
        if default: logger.warning('default given as parameter for %s', json_path)
        try:
            if not config_object: config_object = self._config_object
            return get_by_json_path(config_object, json_path, default)
        except:
            return default

    def get_config_from_documentation_object(self, documentation_object):
        logger.debug('start get_config_from_documentation_object')
        return_array = documentation_object['configuration'] if 'configuration' in documentation_object else []
        for library_name in get_by_json_path(documentation_object, 'libraries', dict()):
            return_array += get_by_json_path(documentation_object['libraries'][library_name], 'configuration', [])
        return return_array

    def get_modul_config(self, module_name, config_object = None, module_documentation= None):
        if not self._config_object: return {}
        if not config_object: config_object = self._config_object
        if not module_documentation: module_documentation = importlib.import_module(module_name+'.docs').DOCUMENTATION
        all_config_keys = self.get_config_from_documentation_object(module_documentation)
        all_config_key_value = self.prepare_module_config(all_config_keys, config_object)
        return all_config_key_value

    def prepare_module_config(self, array_of_config_parameters, config_object):
        return_dict = dict()
        for config_parameter in array_of_config_parameters:
            name = config_parameter['json_path'].split('/').pop()
            value = get_by_json_path(config_object, config_parameter['json_path'])
            #type_name = get_by_json_path(config_object, config_parameter['type'], 'str')
            #if not str(type(value)) ==  type_name:
            #    logger.warning('%s should be %s but is %s', config_parameter['json_path'], type_name, str(type(value)))
            return_dict[name] = value
        return return_dict

    __call__ = get_by_path