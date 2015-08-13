#!/usr/bin/python

import unittest
import httplib
import os
import re
import sys
import subprocess

import dbconf
import dbcreate

testuser = "nelg"
testserver = "localhost:8000"
yubicotesturl = "/wsapi/2.0/verify"
valid_otp = 'hihrhghufvfibbbekurednelnklnulclbiubvjrenlii'
nonce = 'nILSu3qRwoDldXjgU1'



class YubiserveTestCase(unittest.TestCase):
    def setUp(self):
        self.tearDown()
        return yubikey.add(testuser, 'hihrhghufvfi', '676f6e656c67', '89eb6d3d930077b427a88760db0fc375')

    def tearDown(self):
        return yubikey.delete(testuser)


class YubikeyTestCase(YubiserveTestCase):
    def testDbAPIkey(self):
        apikeys = api.list()
        self.assertTrue(len(apikeys) > 0, msg="No API keys in DB")

    def testDbconf(self):
        users = yubikey.list()
        nicknames = [ (nickname, publicid) for nickname, publicid, _ in users ]
        self.assertTrue((testuser, 'hihrhghufvfi') in nicknames)

    def testDisableEnableKey(self):
        yubikey.disable(testuser)
        data = self.curl('?id=1&otp=%s&nonce=%s' % (valid_otp, nonce))
        m = re.search("^status=BAD_OTP", data, re.M)
        self.assertTrue(m, msg="Valid yubikey, but account is disabled")

        yubikey.enable(testuser)
        data = self.curl('?id=1&otp=%s&nonce=%s' % (valid_otp, nonce))
        m = re.search("^status=OK", data, re.M)
        self.assertTrue(m, msg="Valid yubikey not accepted")

    def testReplayKey(self):
        data = self.curl('?id=1&otp=%s&nonce=%s' % (valid_otp, nonce))
        m = re.search("^status=OK", data, re.M)
        self.assertTrue(m, msg="Valid yubikey not accepted")

        data = self.curl('?id=1&otp=%s&nonce=%s' % (valid_otp, nonce))
        m = re.search("^status=REPLAYED_OTP", data, re.M)
        self.assertTrue(m, msg="Replayed token should not be accepted")

    def testbadCRC(self):
        invalid_otp = 'hihrhghufvfirvbegrijgdjhjhtgihcehehtcrgbrhrb'
        data = self.curl('?id=1&otp=%s&nonce=%s' % (invalid_otp, nonce))
        m = re.search("^status=BAD_OTP", data,re.M)
        self.assertTrue(m, msg="Yubikey with Bad CRC")

    def testInvalidInput(self):
        data = self.curl('?id=1&otp=&&&&&&&&&&&&&&&&&&&&&&&&')
        m = re.search("^status=MISSING_PARAMETER", data, re.M)
        self.assertTrue(m, msg="invalid input should not be accepted, otp not set")

    def testInvalidOTP(self):
        invalid_otp = 'hihrhghufvfibbbek1urednelnklnulclbiubvjrenlii'
        data = self.curl('?id=1&otp=%s&nonce=%s' % (invalid_otp, nonce))
        m = re.search("^status=MISSING_PARAMETER", data, re.M)
        self.assertTrue(m, msg="invalid otp (contains a 1)")

    def curl(self, params='?id=1&otp=%s' % valid_otp, debug=False, url=yubicotesturl, httpcode=200):
        conn = httplib.HTTPConnection(testserver)
        conn.request('GET', url + params)
        r = conn.getresponse()
        self.assertTrue(r.status == httpcode)
        data = r.read()
        conn.close()
        if debug:
            print 'Request: %s\n' % (url+params)
            print data
        return data


if __name__ == '__main__':
    filename = '/tmp/yubiservetest.sqlite3'

    # create database
    dbcreate.create_db(filename)

    # add an API key
    api = dbconf.API(filename, verbose=False)
    api.add('test')

    yubikey = dbconf.Yubikey(filename, verbose=False)

    p = subprocess.Popen([ './src/yubiserve.py', '--db', filename ], stderr=open('/dev/null', 'w'))

    suite = unittest.TestLoader().loadTestsFromTestCase(YubikeyTestCase)
    unittest.TextTestRunner().run(suite)

    api.delete('test')
    os.unlink(filename)

    p.kill()
