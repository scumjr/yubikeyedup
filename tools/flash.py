#!/usr/bin/env python3

'''
Write a new AES key to a YubiKey, and store it into a sqlite3 database.
'''

import distutils.spawn
import os
import sys
import subprocess


def hex2modhex(string):
    l = [ ('0123456789abcdef'[i], 'cbdefghijklnrtuv'[i]) for i in range(16) ]
    modhex = ''.join(dict(l).get(chr(j), '?') for j in range(256))
    return string.translate(modhex)

def gen_random(size):
    with open('/dev/urandom','rb') as fp:
        s = fp.read(size)
    return s

def get_public(name):
    return name.rjust(8, 'q')[:8]

if __name__ == '__main__':
    if len(sys.argv) != 3:
        print('Usage: %s <name> <db.sqlite3>' % sys.argv[0])
        print('eg: %s bobama db/yubikeys.sqlite3' % sys.argv[0])
        sys.exit(0)

    name = sys.argv[1]
    db = sys.argv[2]
    aeskey = gen_random(16).hex()
    public = get_public(name).encode('utf-8').hex()
    public_m = hex2modhex(public)
    uid = gen_random(6).hex()

    cmd = [ 'ykpersonalize',
            '-1',
            '-ofixed=h:%s' % public,
            '-ouid=%s' % uid,
            '-a%s' % aeskey
    ]

    print(cmd)

    # prefer sudo over running this script with root privileges
    if os.getuid() != 0:
        if not distutils.spawn.find_executable('sudo'):
            print('Root privileges required.')
            sys.exit(1)
        cmd = [ 'sudo' ] + cmd

    try:
        ret = subprocess.call(cmd)
    except OSError as e:
        if e.errno == os.errno.ENOENT:
            print('%s: command not found.' % cmd[0])
            sys.exit(1)
        else:
            raise

    # if ret != 0:
    #     sys.exit(ret)

    cwd = os.path.dirname(os.path.realpath(__file__))
    dbconf = os.path.join(cwd, 'dbconf.py')
    subprocess.call([ dbconf, '-yk', name, db ])
    subprocess.call([ dbconf, '-ya', name, public_m, uid, aeskey, db ])
    subprocess.call([ dbconf, '-yl', db])
