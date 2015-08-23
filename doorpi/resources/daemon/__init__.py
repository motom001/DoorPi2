# -*- coding: utf-8 -*-

import main
logger = main.DOORPI.register_modul(__name__)

def load_daemon_libs():
    try:
        from daemon import runner
        from daemon.runner import DaemonRunnerInvalidActionError
        from daemon.runner import DaemonRunnerStartFailureError
        from daemon.runner import DaemonRunnerStopFailureError
        return True
    except ImportError as exp:
        return False

DAEMON_AVAILABLE = load_daemon_libs()
