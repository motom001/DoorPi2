#!/usr/bin/python
# -*- coding: utf-8 -*-


# system modules
import os
import argparse
import logging
import logging.handlers
try:
    from daemon import runner
    from daemon.runner import DaemonRunnerInvalidActionError
    from daemon.runner import DaemonRunnerStartFailureError
    from daemon.runner import DaemonRunnerStopFailureError
    daemon_possible = True
except ImportError as exp:
    daemon_possible = exp

# self-import to prevent recursiv imports later
import main

import resources.constants as CONST
from resources.logging import init_own_logger
logging.basicConfig(level = logging.ERROR, format = CONST.LOG_FORMAT)
logger = init_own_logger(__name__)

# doorpi modules and doorpi itself
from resources.singleton import Singleton
from resources.core import DoorPi
from resources.functions.filesystem import get_base_dir

DOORPI = DoorPi()
BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_string(raw_string, **kwargs):
    var_dict = globals()
    var_dict.update(map(dict, kwargs))
    for var in var_dict:
        try:    raw_string = raw_string.replace(var, var_dict[var])
        except: pass
    return raw_string

if __name__ == '__main__':
    possible_loglevels = map(logging.getLevelName, range(0, 51, 10))

    parser = argparse.ArgumentParser(description = ' - '.join([CONST.META.prog, CONST.META.project]))
    parser.add_argument('-log_level', default = CONST.LOG_LEVEL, action='store', dest = "log_level", choices = possible_loglevels, help = "Set the logging level for console output")
    parser.add_argument("-d", "--daemon", dest = "daemon", default = 'NONE', choices = ['START', 'STOP', 'RESTART'], help = "daemon control - NONE to start as application")
    parser.add_argument('--logfile', default = CONST.LOG_DEFAULT_FILENAME, dest = "log_file", type = file, help = 'Logfile with rotating file handler')
    parser.add_argument("--logfile_level", default = CONST.LOG_LEVEL, action = "store", dest = "logfile_level", choices = possible_loglevels, help = "Set the logging level for the logfile")
    parser.add_argument("--logfile_maxBytes", default = 50000, dest = "logfile_max_bytes", type = int, help = "Set the logfile max size (each rotated file)")
    parser.add_argument("--logfile_maxFiles", default = 10, dest = "logfile_max_files", type = int, help = "Set the logfile max rotation")
    parser.add_argument("--skip_sudo_check", default = False, action = "store_true", dest = "skip_sudo_check", help = "if set DoorPi will not check sudo or root access and you have to configure the rights by yourself")
    args = parser.parse_args()

    if os.geteuid() != 0 and args.skip_sudo_check is False: raise SystemExit("DoorPi must run with sudo rights - maybe use --skip_sudo_check to skip this check")

    CONST.LOG_LEVEL = args.log_level
    logging.getLogger('').setLevel(CONST.LOG_LEVEL)

    DOORPI.prepare()
    DOORPI.logger.setLevel(CONST.LOG_LEVEL)
    DOORPI.logger.setFormatter(logging.Formatter(CONST.LOG_FORMAT))
    logging.getLogger('').addHandler(DOORPI.logger)

    if args.log_file:
        try:
            logrotating = logging.handlers.RotatingFileHandler(
                  args.log_file.name,
                  maxBytes = args.logfile_max_bytes,
                  backupCount = args.logfile_max_files
            )
            logrotating.setLevel(args.logfile_level)
            logrotating.setFormatter(logging.Formatter(CONST.LOG_FORMAT))
            logging.getLogger('').addHandler(logrotating)
        except IOError as exp:
            logging.exception("Managed exception while open logfile %s"%exp)

    logger = init_own_logger(__name__)

    logger.info(CONST.META.epilog)
    logger.debug('loaded with arguments: %s', str(args))

    if daemon_possible is not True:
        logger.error("Daemon-Mode ist not possible - switch back to application mode. Laste Exception was '%s'"%daemon_possible)

        try:                        DOORPI.run()
        except KeyboardInterrupt:   logger.info("KeyboardInterrupt -> DoorPi will shutdown")
        except Exception as ex:     logger.exception("Exception NameError: %s", ex)
        finally:                    DOORPI.destroy()

    logger.info('finished')
