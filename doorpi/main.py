#!/usr/bin/python
# -*- coding: utf-8 -*-

# system modules
import os, platform
import sys
import argparse
import logging
import logging.handlers

# self-import to prevent recursiv imports later
import main

# doorpi modules and doorpi itself
import resources.constants as CONST
from resources.singleton import Singleton
from resources.core import DoorPi
DOORPI = Singleton(DoorPi)

from resources.logging import init_own_logger
logging.basicConfig(level = logging.DEBUG, format = CONST.LOG_FORMAT)
logger = init_own_logger(__name__)

import resources.daemon as DAEMON

BASE_PATH = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))

def parse_string(raw_string, kwargs = None):
    var_dict = globals()
    if kwargs: var_dict.update(kwargs)
    for var in var_dict:
        try:    raw_string = raw_string.replace('!'+var+'!', var_dict[var])
        except: pass
    return raw_string

if __name__ == '__main__':
    possible_loglevels = map(logging.getLevelName, range(0, 51, 10))
    possible_daemon_commands = ['start', 'stop', 'restart']

    parser = argparse.ArgumentParser(description = ' - '.join([CONST.META.prog, CONST.META.project]))
    parser.add_argument("daemon", default = 'NONE', choices = possible_daemon_commands + ['NONE'], help = "daemon control - NONE to start as application", nargs = '?')
    parser.add_argument('--log_level', default = CONST.LOG_LEVEL, action='store', dest = "log_level", choices = possible_loglevels, help = "Set the logging level for console output")
    parser.add_argument('--logfile', default = CONST.LOG_DEFAULT_FILENAME, dest = "log_file", help = 'Logfile with rotating file handler')
    parser.add_argument("--logfile_level", default = CONST.LOG_LEVEL, action = "store", dest = "logfile_level", choices = possible_loglevels, help = "Set the logging level for the logfile")
    parser.add_argument("--logfile_maxBytes", default = 5000000, dest = "logfile_max_bytes", type = int, help = "Set the logfile max size (each rotated file)")
    parser.add_argument("--logfile_maxFiles", default = 10, dest = "logfile_max_files", type = int, help = "Set the logfile max rotation")
    parser.add_argument("--skip_sudo_check", default = False, action = "store_true", dest = "skip_sudo_check", help = "if set DoorPi will not check sudo or root access and you have to configure the rights by yourself")
    parser.add_argument("--install_daemon", default = False, action = "store_true", dest = "install_daemon", help = "install daemonfile, pip modul 'python-daemon' and register the daemonfile")
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

    logger.info(CONST.META.epilog)
    logger.debug('loaded with arguments: %s', str(args))

    #from resources.daemon.install import reinstall as daemon_auto_installer
    #daemon_auto_installer()

    if args.daemon in possible_daemon_commands or args.install_daemon:
        if args.daemon in sys.argv and sys.argv[1] != args.daemon:
            sys.argv.remove(args.daemon)
            sys.argv = [sys.argv[0], args.daemon] + sys.argv[1:]
        if DAEMON.DAEMON_AVAILABLE is not True:
            from resources.daemon.install import install as daemon_auto_installer
            try:
                daemon_auto_installer()
                logger.info('installed daemon for DoorPi - restart DoorPi now')
                os.execv(sys.argv[0], sys.argv)
            except OSError as exp:
                raise SystemExit("restart of DoorPi failed - please restart it")
            except Exception as exp:
                raise SystemExit("error during autoinstaller: '%s'"%exp)
        elif args.install_daemon:
            sys.argv.remove('--install_daemon')

            from resources.daemon.install import reinstall as daemon_auto_reinstaller
            try:
                daemon_auto_reinstaller()
                logger.info('reinstalled daemon for DoorPi - restart DoorPi now')
                os.execv(sys.argv[0], sys.argv)
            except OSError as exp:
                raise SystemExit("restart of DoorPi failed ('%s') - please restart it"%exp)
            except Exception as exp:
                raise SystemExit("error during autoreinstaller: '%s'"%exp)
        from daemon import runner
        from daemon.runner import DaemonRunnerInvalidActionError
        from daemon.runner import DaemonRunnerStartFailureError
        from daemon.runner import DaemonRunnerStopFailureError
        from resources.functions.filesystem import files_preserve_by_path
        daemon_runner = runner.DaemonRunner(DOORPI)
        if args.log_file: daemon_runner.daemon_context.files_preserve = files_preserve_by_path(args.log_file)
    else:
        from resources.daemon.install import DaemonRunnerInvalidActionError
        from resources.daemon.install import DaemonRunnerStartFailureError
        from resources.daemon.install import DaemonRunnerStopFailureError

    try:
        if args.daemon in possible_daemon_commands:         daemon_runner.do_action()
        else:                                               DOORPI.start(start_as_daemon = False)
    except DaemonRunnerStartFailureError as ex:             logger.error("can't start DoorPi daemon - maybe it's running already? (Message: %s)", ex)
    except DaemonRunnerStopFailureError as ex:              logger.error("can't stop DoorPi daemon - maybe it's not running? (Message: %s)", ex)
    except KeyboardInterrupt:                               logger.info("KeyboardInterrupt -> DoorPi will shutdown")
    except Exception as ex:                                 logger.exception("Exception: %s", ex)
    finally:                                                DOORPI.stop()

    logger.info('finished')
