# -*- coding: utf-8 -*-

import os
from resource import getrlimit, RLIMIT_NOFILE

def get_base_dir(file):
    os.path.dirname(os.path.dirname(os.path.abspath(file)))

def files_preserve_by_path(*paths):
    wanted=[]
    for path in paths:
        fd = os.open(path, os.O_RDONLY)
        try:
            wanted.append(os.fstat(fd)[1:3])
        finally:
            os.close(fd)

    def fd_wanted(fd):
        try:
            return os.fstat(fd)[1:3] in wanted
        except OSError:
            return False

    fd_max = getrlimit(RLIMIT_NOFILE)[1]
    return [ fd for fd in xrange(fd_max) if fd_wanted(fd) ]
