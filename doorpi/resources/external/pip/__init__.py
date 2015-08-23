# -*- coding: utf-8 -*-

from main import DOORPI
logger = DOORPI.register_modul(__name__)

class PipNotAvailableException(Exception): pass

try:
    import pip
    PIP_AVAILABLE = True
except ImportError as exp:
    PIP_AVAILABLE = False

def install(package):
    if not PIP_AVAILABLE: raise PipNotAvailableException()
    logger.info('try to install pip package %s', package)
    return pip.main(['install', package])

def update(package):
    return False

def uninstall(package):
    if not PIP_AVAILABLE: raise PipNotAvailableException()
    logger.warning('try to uninstall pip package %s', package)
    return pip.main(['uninstall', 'y', package])
