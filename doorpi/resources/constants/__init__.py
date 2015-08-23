# -*- coding: utf-8 -*-

# section META from metadata
import resources.metadata.core as META

# section LOG
LOG_LEVEL = 'DEBUG'
LOG_FORMAT = '%(asctime)s [%(levelname)s]  \t[%(name)s] %(message)s'
LOG_DEFAULT_FILENAME = '/var/log/doorpi/doorpi.log'

# section CONFIG
CONFIG_DEFAULT_FILENAME = '!BASE_PATH!/config/_current.json'

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
