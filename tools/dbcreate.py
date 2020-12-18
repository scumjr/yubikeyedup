#!/usr/bin/env python3

import os
import sqlite3
import sys

TABLES = [
'''yubikeys(
 nickname varchar(16) unique not null,
 publicname varchar(16) unique not null,
 created varchar(24) not null,
 internalname varchar(12) not null,
 aeskey varchar(32) not null,
 active boolean default true,
 counter integer not null default 1,
 time integer not null default 1
)''',
'''oathtokens(
 nickname varchar(16) unique not null,
 publicname varchar(12) unique not null,
 created varchar(24) not null,
 secret varchar(40) not null,
 active boolean default true,
 counter integer not null default 1
)''',
'''apikeys(
 nickname varchar(16),
 secret varchar(28),
 id integer primary key
)''',
]

def create_db(filename):
    if os.path.exists(filename):
        print('%s already exists' % filename)
        sys.exit(1)

    conn = sqlite3.connect(filename)
    c = conn.cursor()
    for table in TABLES:
        c.execute('CREATE TABLE %s' % table)
    conn.commit()
    conn.close()

if __name__ == '__main__':
    if len(sys.argv) != 2:
        print('Usage: %s <db.sqlite3>' % sys.argv[0])
        sys.exit(0)

    create_db(sys.argv[1])
