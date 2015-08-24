# -*- coding: utf-8 -*-

# section META from metadata
import resources.metadata.core as META

# section LOG
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s'
LOG_DEFAULT_FILENAME = '/var/log/doorpi/doorpi.log'

# section CONFIG
CONFIG_DEFAULT_FILENAME = '!BASE_PATH!/config/doorpi.json'
CONFIG_LAST_WORKING_FILENAME = '!BASE_PATH!/config/_last_working_doorpi_config.json'

# section daemon
DAEMON_STDIN_PATH = '/dev/null'
DAEMON_STDOUT_PATH = '/dev/null'
DAEMON_STDERR_PATH = '/dev/null'
DAEMON_PIDFILE = '/var/run/doorpi.pid'
DAEMON_PIDFILE_TIMEOUT = 5

DAEMON_FILE = {
    'Linux': {'source': '!BASE_PATH!/docs/service/linux.daemon.example', 'target': '/etc/init.d/doorpi', 'uninstall_command': 'update-rc.d doorpi remove', 'install_command': 'update-rc.d doorpi defaults'}
}

DAEMON_DEFAULT_ARGUMENTS = "--logfile "+LOG_DEFAULT_FILENAME

EVENTHANDLER_DB_TYP = 'sqlite'
EVENTHANDLER_DB_CONNECTIONSTRING = '!BASE_PATH!/conf/event_log.db'

USED_PYTHON_VERSION = ''

PIP_GENERAL_DEFAULT_ARGUMENTS = ['--disable-pip-version-check', '-q']
PIP_NOT_INSTALLED_ERROR = 'https://github.com/motom001/DoorPi/wiki/FAQ#wie-installiere-ich-pip'