#!/usr/bin/env python


import stat
import os
from os import walk
from os.path import join

EXEC_WHITELIST = [
    '.git/',
    'test/',
    'docs/',
    'contrib/inventory/',
    'bin/',
    'examples/',
    'hacking/',
    'packaging/debian/rules',
    'plugins/inventory/',
]

CHECK_BASE_DIR = 'lib/ansible'


def is_executable(path):
    '''is the given path executable?

    Limitations:
    * Does not account for FSACLs.
    * Most times we really want to know "Can the current user execute this
      file"  This function does not tell us that, only if an execute bit is set.
    '''
    # These are all bitfields so first bitwise-or all the permissions we're
    # looking for, then bitwise-and with the file's mode to determine if any
    # execute bits are set.
    return ((stat.S_IXUSR | stat.S_IXGRP | stat.S_IXOTH) & os.stat(path)[stat.ST_MODE])


def main():

    scandir = os.path.normpath(os.path.realpath(os.path.expanduser(os.path.expandvars(CHECK_BASE_DIR))))
    executable_files = []

    for root, dirs, files in walk(scandir):
        if files:
            for f in files:
                for whitelist_path in EXEC_WHITELIST:
                    if whitelist_path in join(root, f):
                        break
                else:
                    if is_executable(join(root, f)):
                        executable_files.append(join(root, f))

    if executable_files:
        print("Following files are executable:")
        print("\n".join(executable_files))
        exit(1)
    else:
        exit(0)

if __name__ == '__main__':
    main()
