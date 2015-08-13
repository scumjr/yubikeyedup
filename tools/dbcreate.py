#!/usr/bin/env python

import os
import subprocess
import sys

SCHEMA = '''
BEGIN TRANSACTION;
create table yubikeys(
 nickname varchar(16) unique not null,
 publicname varchar(16) unique not null,
 created varchar(24) not null,
 internalname varchar(12) not null,
 aeskey varchar(32) not null,
 active boolean default true,
 counter integer not null default 1,
 time integer not null default 1
);
create table oathtokens(
 nickname varchar(16) unique not null,
 publicname varchar(12) unique not null,
 created varchar(24) not null,
 secret varchar(40) not null,
 active boolean default true,
 counter integer not null default 1
);
create table apikeys(
 nickname varchar(16),
 secret varchar(28),
 id integer primary key
);
COMMIT;
'''

def create_db(filename):
    if os.path.exists(filename):
        print '%s already exists' % filename
        sys.exit(1)

    p = subprocess.Popen([ 'sqlite3', filename ], stdin=subprocess.PIPE)
    p.stdin.write(SCHEMA)
    p.stdin.close()

    if p.wait() != 0:
        print 'failed to create %s' % filename
        sys.exit(1)


if __name__ == '__main__':
    if len(sys.argv) != 2:
	print 'Usage: %s <db.sqlite3>' % sys.argv[0]
        sys.exit(0)

    create_db(sys.argv[1])
