# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_module(__name__, return_new_logger = True)

def get_by_json_path(json_object, json_path, default = ''):
    try:
        json_path_steps = json_path.split('/')
        json_path_first_step = json_path_steps[0]
        if len(json_path_steps) > 1:
            json_path_tail = json_path_steps[1:]
            return get_by_json_path(json_object[json_path_first_step], '/'.join(json_path_tail))
        logger.debug('json_path %s returns %s', json_path, json_object[json_path_first_step])
        return json_object[json_path_first_step]
    except Exception as exp:
        logger.warning('json_path %s not found and return default %s (error: %s)', json_path, default, exp)
        return default
