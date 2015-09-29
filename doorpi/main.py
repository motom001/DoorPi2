#!/usr/bin/python
# -*- coding: utf-8 -*-

# system modules
import os, platform
import sys
import argparse
import logging
import logging.handlers

# self-import to prevent endless imports later
import main

# doorpi modules and doorpi itself
import resources.constants as CONST
from resources.singleton import Singleton
from resources.core import DoorPi, CorruptConfigFileException
DOORPI = Singleton(DoorPi)

from resources.logging import init_own_logger
logging.basicConfig(level=logging.DEBUG, format=CONST.LOG_FORMAT)
logger = init_own_logger(__name__)

import resources.daemon as DAEMON
from resources.auto_install import install as auto_install, uninstall as auto_uninstall

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
CONST.USED_PYTHON_VERSION = "%s.%s"%(sys.version_info.major, sys.version_info.minor)

def parse_string(raw_string, kwargs = None):
    var_dict = globals()
    if kwargs: var_dict.update(kwargs)
    for var in var_dict:
        try:    raw_string = raw_string.replace('!'+var+'!', var_dict[var])
        except: pass
    return raw_string

def entry_point():
    print(CONST.META.epilog)

    possible_loglevels = map(logging.getLevelName, range(0, 51, 10))
    possible_daemon_commands = ['start', 'stop', 'restart']

    parser = argparse.ArgumentParser(description = ' - '.join([CONST.META.prog, CONST.META.project]))
    parser.add_argument("daemon", default = 'NONE', choices = possible_daemon_commands + ['NONE'], help = "daemon control - NONE to start as application", nargs = '?')
    parser.add_argument('-c', '--configfile', default = CONST.CONFIG_DEFAULT_FILENAME, dest = "config_file", help = 'configfile in json')
    parser.add_argument('--log_level', default = CONST.LOG_LEVEL, action='store', dest = "log_level", choices = possible_loglevels, help = "Set the logging level for console output")
    parser.add_argument('--logfile', default = CONST.LOG_DEFAULT_FILENAME, dest = "log_file", help = 'Logfile with rotating file handler')
    parser.add_argument("--logfile_level", default = CONST.LOG_LEVEL, action = "store", dest = "logfile_level", choices = possible_loglevels, help = "Set the logging level for the logfile")
    parser.add_argument("--logfile_maxBytes", default = 5000000, dest = "logfile_max_bytes", type = int, help = "Set the logfile max size (each rotated file)")
    parser.add_argument("--logfile_maxFiles", default = 10, dest = "logfile_max_files", type = int, help = "Set the logfile max rotation")
    parser.add_argument("--skip_sudo_check", default = False, action = "store_true", dest = "skip_sudo_check", help = "if set DoorPi will not check sudo or root access and you have to configure the rights by yourself")
    parser.add_argument("--install_daemon", default = False, action = "store_true", dest = "install_daemon", help = "install daemonfile, pip modul 'python-daemon' and register the daemonfile")
    #parser.add_argument("--use_last_known_config", default = False, action = "store_true", dest = "use_last_known_config", help = "use the last known working config")
    args = parser.parse_args()

    if os.geteuid() != 0 and args.skip_sudo_check is False: raise SystemExit("DoorPi must run with sudo rights - maybe use --skip_sudo_check to skip this check")

    CONST.LOG_LEVEL = args.log_level
    logging.getLogger('').setLevel(CONST.LOG_LEVEL)

    DOORPI.prepare(args)
    DOORPI.logger.setLevel(CONST.LOG_LEVEL)
    DOORPI.logger.setFormatter(logging.Formatter(CONST.LOG_FORMAT))
    logging.getLogger('').addHandler(DOORPI.logger)

    if args.log_file:
        try:
            logrotating = logging.handlers.RotatingFileHandler(
                  args.log_file,
                  maxBytes = args.logfile_max_bytes,
                  backupCount = args.logfile_max_files
            )
            logrotating.setLevel(args.logfile_level)
            logrotating.setFormatter(logging.Formatter(CONST.LOG_FORMAT))
            logging.getLogger('').addHandler(logrotating)
        except IOError as exp:
            logging.exception("Managed exception while open logfile %s"%exp)

    logger = init_own_logger(__name__)
    logger.debug('loaded with arguments: %s', str(args))

    if args.daemon in possible_daemon_commands or args.install_daemon:
        if args.daemon in sys.argv and sys.argv[1] != args.daemon:
            sys.argv.remove(args.daemon)
            sys.argv = [sys.argv[0], args.daemon] + sys.argv[1:]

        if not DAEMON.DAEMON_AVAILABLE or args.install_daemon:
            try:
                if args.install_daemon:
                    sys.argv.remove('--install_daemon')
                    auto_uninstall('resources.daemon')
                auto_install('resources.daemon')
                logger.info('installed daemon for DoorPi - restart DoorPi now')
                os.execv(sys.argv[0], sys.argv)
            except OSError as exp:
                raise SystemExit("restart of DoorPi failed - please restart it")
            except Exception as exp:
                raise SystemExit("error during autoinstaller: '%s'"%exp)

        from daemon import runner
        from daemon.runner import DaemonRunnerInvalidActionError
        from daemon.runner import DaemonRunnerStartFailureError
        from daemon.runner import DaemonRunnerStopFailureError
        from resources.functions.filesystem import files_preserve_by_path
        daemon_runner = runner.DaemonRunner(DOORPI)
        if args.log_file: daemon_runner.daemon_context.files_preserve = files_preserve_by_path(args.log_file)
    else:
        from resources.daemon import DaemonRunnerInvalidActionError
        from resources.daemon import DaemonRunnerStartFailureError
        from resources.daemon import DaemonRunnerStopFailureError

    try:
        if args.daemon in possible_daemon_commands:         daemon_runner.do_action()
        else:                                               DOORPI.start(start_as_daemon = False)
    except DaemonRunnerStartFailureError as ex:             logger.error("can't start DoorPi daemon - maybe it's running already? (Message: %s)", ex)
    except DaemonRunnerStopFailureError as ex:              logger.error("can't stop DoorPi daemon - maybe it's not running? (Message: %s)", ex)
    except KeyboardInterrupt:                               logger.info("KeyboardInterrupt -> DoorPi will shutdown")
    except CorruptConfigFileException as ex:                logger.exception("CorruptConfigFileException: %s", ex)
    except Exception as ex:                                 logger.exception("Exception: %s", ex)
    finally:                                                DOORPI.stop()

    logger.info('finished')

if __name__ == '__main__':
    raise SystemExit(entry_point())
