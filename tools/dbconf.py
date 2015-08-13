#!/usr/bin/env python

'''
YubiServe Key Management Tool
'''

import os
import random
import re
import sqlite3
import sys
import time


def randomChars(size):
    alphabet  = [ chr(i) for i in range(ord('a'), ord('z')+1) ]
    alphabet += [ chr(i) for i in range(ord('A'), ord('Z')+1) ]
    alphabet += [ chr(i) for i in range(ord('0'), ord('9')+1) ]

    return ''.join(random.choice(alphabet) for i in range(size))


def usage():
    print 'Usage: %s <options> <db.sqlite3>\n' % sys.argv[0]
    print ' -ya <nickname> <publicid> <secretid> <aeskey>\tAdd a new Yubikey'
    print ' -yk <nickname>\t\t\t\t\tDelete a Yubikey'
    print ' -yd <nickname>\t\t\t\t\tDisable a Yubikey'
    print ' -ye <nickname>\t\t\t\t\tEnable a Yubikey'
    print ' -yl\t\t\t\t\t\tList all yubikeys in database\n'

    print ' -ha <nickname> <publicid> <key>\t\tAdd a new OATH token'
    print ' -hk <nickname>\t\t\t\t\tDelete a OATH token'
    print ' -hd <nickname>\t\t\t\t\tDisable a OATH token'
    print ' -he <nickname>\t\t\t\t\tEnable a OATH token'
    print ' -hl\t\t\t\t\t\tList all OATH tokens in database\n'

    print ' -aa <keyname>\t\t\t\t\tGenerate an API Key'
    print ' -ak <keyname>\t\t\t\t\tRemove an API Key'
    print ' -al\t\t\t\t\t\tList all API Keys in database'

    sys.exit(0)


class DBConf:
    REQUESTS = {
        'y_get_active':		'SELECT active FROM yubikeys WHERE nickname = ?',
        'y_set_active':		'UPDATE yubikeys SET active = ? WHERE nickname = ?',
        'y_delete':		'DELETE FROM yubikeys WHERE nickname = ?',
        'y_count_nickname':	'SELECT count(nickname) FROM yubikeys WHERE nickname = ? OR publicname = ?',
        'y_add':		'INSERT INTO yubikeys VALUES (?, ?, ?, ?, ?, 1, 1, 1)',

        'oath_get_active':	'SELECT active FROM oathtokens WHERE nickname = ?',
        'oath_set_active':	'UPDATE oathtokens SET active = ? WHERE nickname = ?',
        'oath_delete':		'DELETE FROM oathtokens WHERE nickname = ?',
        'oath_count_nickname':	'SELECT count(nickname) FROM oathtokens WHERE nickname = ? OR publicname = ?',
        'oath_add':		'INSERT INTO oathtokens VALUES (?, ?, ?, ?, 1, 1)',

        'api_count_nickname':	'SELECT count(nickname) FROM apikeys WHERE nickname = ?',
        'api_count_nicknames':	'SELECT count(nickname) FROM apikeys',
        'api_get_last_id':	'SELECT id FROM apikeys ORDER BY id DESC LIMIT 1',
        'api_add':		'INSERT INTO apikeys VALUES (?, ?, ?)',
    }

    def __init__(self, filename, verbose=True):
        self.con = sqlite3.connect(filename)
        self.cur = self.con.cursor()
        self.verbose = verbose

    def select(self, req, param):
        self.cur.execute(self.REQUESTS[req], param)
        self.result = self.cur.fetchone()
        return self.result != None

    def update(self, req, param):
        self.con.execute(self.REQUESTS[req], param)
        self.con.commit()

    def log(self, msg):
        if self.verbose:
            print msg


class Yubikey(DBConf):
    def add(self, nickname, publicid, secretid, aeskey):
        if len(nickname) > 16 or len(publicid) > 16 or len(secretid) > 12 or len(aeskey) > 32:
            print 'Nickname and publicid must be max 16 characters long.'
            print 'Secretid must be 12 characters max, aeskey must be 32 characters max.'
            return -1

        self.select('y_count_nickname', [nickname, publicid])
        if self.result[0] != 0:
            self.log('Key is already into database. Delete it before adding the same key!')
            return -1

        t = time.strftime('%Y-%m-%dT%H:%M:%SZ', time.gmtime())
        self.update('y_add', [ nickname, publicid, t, secretid, aeskey ])
        self.log('Key %s added to database.' % nickname)

    def delete(self, nickname):
        if not self.select('y_get_active', [ nickname ]):
            self.log('Key not found.')
            return -1

        self.update('y_delete', [ nickname ])
        self.log('Key %s deleted.' % nickname)

    def disable(self, nickname):
        if not self.select('y_get_active', [ nickname ]):
            self.log('Key not found.')
            return -1

        active = self.result[0]
        if not active:
            self.log('Key is already disabled.')
            return 0

        self.update('y_set_active', [ 0, nickname ])
        self.log('Key %s disabled.' % nickname)

    def enable(self, nickname):
        if not self.select('y_get_active', [ nickname ]):
            self.log('Key not found.')
            return -1

        active = self.result[0]
        if active:
            self.log('Key is already enabled.')
            return 0

        self.update('y_set_active', [ 1, nickname ])
        self.log('Key %s enabled.' % nickname)

    def list(self):
        self.cur.execute('SELECT count(nickname) FROM yubikeys')
        rowcount = self.cur.fetchone()
        self.log('%d keys into database:' % rowcount[0])

        users = []
        if rowcount[0]:
            self.cur.execute('SELECT nickname, publicname, active FROM yubikeys')
            self.log('[Nickname]\t\t>> [PublicID]\t\t>> [Active]')
            for nickname, publicname, active in self.cur:
                self.log('%-23s >> %-20s >> %s ' %  (nickname, publicname, active))
                users.append((nickname, publicname, active))

        return users

class OATH(DBConf):
    def add(self, nickname, publicid, key):
        if len(nickname) > 16 or len(publicid) > 16 or len(key) > 40:
            print 'Nickname and publicid must be max 16 characters long.'
            print 'Secret key must be 40 characters max.'
            return -1

        self.select('oath_count_nickname', [nickname, publicid])
        if self.result[0] != 0:
            self.log('Key is already into database. Delete it before adding the same key!')
            return -1

        t = time.strftime("%Y-%m-%dT%H:%M:%SZ", time.gmtime())
        self.update('INSERT INTO oathtokens VALUES (?, ?, ?, ?, 1, 1)', [nickname, publicid, t, key])
        self.log('Key "%s" added to database.' % key)

    def disable(self, nickname):
        if not self.select('oath_get_active', [ nickname ]):
            self.log('Key not found.')
            return -1

        active = self.result[0]
        if not active:
            self.log('Key is already disabled.')
            return 0

        self.update('oath_set_active', [ 0, nickname ])
        self.log('Key %s disabled.' % nickname)

    def enable(self, nickname):
        if not self.select('oath_get_active', [ nickname ]):
            self.log('Key not found.')
            return -1

        active = self.result[0]
        if active:
            self.log('Key is already enabled.')
            return 0

        self.update('oath_set_active', [ 1, nickname ])
        self.log('Key %s enabled.' % nickname)

    def delete(self, nickname):
        if not self.select('oath_get_active', [ nickname ]):
            self.log('Key not found.')
            return -1

        self.update('y_delete', [ nickname ])
        self.log('Key %s deleted.' % nickname)

    def list(self):
        cur.execute('SELECT count(nickname) FROM oathtokens')
        rowcount = cur.fetchone()
        self.log(" %d keys into database:" % rowcount[0])

        if rowcount[0] != 0:
            cur.execute('SELECT nickname, publicname, active FROM oathtokens')
            self.log('[Nickname]\t\t>> [PublicID]')
            for (nickname, publicname,active) in cur:
                self.log('%-23s >> %-21s >> %s ' % (nickname, publicname, active))

class API(DBConf):
    def add(self, nickname):
        self.select('api_count_nickname', [nickname])
        if self.result[0] != 0:
            self.log('API Key for this nickname is already present. Remove it or choose another one.')
            return -1

        if not self.select('api_get_last_id', []):
            id = 1
        else:
            lastid = self.result[0]
            id = lastid + 1

        api_key = randomChars(20)
        self.update('api_add', [nickname, api_key, id])
        self.log('New API Key for %s: %s' % (nickname, api_key.encode('base64').strip()))
        self.log('Your API Key ID is: %d' % id)

    def delete(self, nickname):
        self.select('api_count_nickname', [nickname])
        if self.result[0] == 0:
            self.log("API Key for this nickname doesn't exists!")
            return -1

        self.cur.execute('DELETE FROM apikeys WHERE nickname = ?', [nickname])
        self.con.commit()
        self.log('API Key for %s has been deleted.' % nickname)

    def list(self):
        self.select('api_count_nicknames', [])
        rowcount = self.result[0]
        self.log('%d keys into database:' % rowcount)

        keys = []
        if rowcount != 0:
            self.cur.execute('SELECT id, nickname, secret FROM apikeys')
            self.log('[Id]\t>> [Keyname]\t\t>> [Secret]')
            for id, nickname, secret in self.cur:
                self.log('%-7d >> %-20s >> %s' % (id, nickname, secret))
                keys.append((id, nickname, secret))
        else:
            self.log('No keys in database')
        return keys


if __name__ == '__main__':
    options = {
        '-ya': (4, Yubikey, 'add'),
        '-yk': (1, Yubikey, 'delete'),
        '-yd': (1, Yubikey, 'disable'),
        '-ye': (1, Yubikey, 'enable'),
        '-yl': (0, Yubikey, 'list'),

        '-ha': (3, OATH, 'add'),
        '-hk': (1, OATH, 'delete'),
        '-hd': (1, OATH, 'disable'),
        '-he': (1, OATH, 'enable'),
        '-hl': (0, OATH, 'list'),

        '-aa': (1, API, 'add'),
        '-ak': (1, API, 'delete'),
        '-al': (0, API, 'list'),
    }

    argv = sys.argv[1:]
    if len(argv) == 0:
        usage()

    if not options.has_key(argv[0]):
        usage()

    n, klass, fname = options[argv[0]]
    if len(argv[1:]) != n + 1:
        usage()

    filename = argv[-1]
    if not os.path.exists(filename):
        print 'SQLite database "%s" doesn\'t exist' % filename
        sys.exit(1)

    args = argv[1:-1]
    function = getattr(klass, fname)
    db = klass(filename)
    function(db, *args)
