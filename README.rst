Yet Another YubiKey OTP Validation Server
=========================================

Several other implementations are available. Some of them are not secure enough:

 * `YubiServe <https://code.google.com/p/yubico-yubiserve>`_ (Python). `SQL
   injections
   <https://code.google.com/p/yubico-yubiserve/issues/detail?id=38>`_,
 * `yubiserver <http://www.include.gr/debian/yubiserver/>`_ (C). SQL injections
   (CVE-2015-0842), buffer overflows (CVE-2015-0843).

Official implementation is written in PHP (sigh...), and I don't know Go enough
to audit digintLab's implementation:

 * `yubikey-val <https://developers.yubico.com/yubikey-val/>`_ (PHP) by Yubico,
 * `yubikey-server <https://github.com/digintLab/yubikey-server>`_ (Go).

This is a complete rewrite of `YubiServe
<https://code.google.com/p/yubico-yubiserve>`_ because the original project
seems not to be designed with security in mind. Copy-and-paste programming made
code reviews nearly impossible, there is no protection against SQL injection,
etc.

This fork was given a new name to make it easy for people to differentiate from
the original project.


Usage
=====

Create a new database::

    $ ./tools/dbcreate.py ./yubikeys.sqlite3

Plug and flash the YubiKeys (keys are also written to the database)::

    $ ./tools/flash.py gbush ./yubikeys.sqlite3
    $ ./tools/flash.py bobama ./yubikeys.sqlite3

Add a new API key (here, the API key name is ``developers``)::

    $ ./tools/dbconf.py -aa developers ./yubikeys.sqlite3

Run the server::

    $ ./src/yubiserve.py --db ./yubikeys.sqlite3

That's it. The servers wanting to make use of two factor authentication need to
be configured. The following paragraph shows an example for OpenSSH.


OpenSSH configuration example
=============================

Here's a summary of `Yubico's documentation
<https://developers.yubico.com/yubico-pam/Yubikey_and_SSH_via_PAM.html>`_.

Get information about users and API on the machine hosting
``yubikeys.sqlite3``::

    $ ./tools/dbconf.py -yl ./yubikeys.sqlite3
    2 keys into database:
    [Nickname]              >> [PublicID]            >> [Active]
    gbush                   >> ibhdhehrhkhuifhv      >> 1
    bobama                  >> ibibhdhvhdhbhthb      >> 1
    
    $ ./tools/dbconf.py -al ./yubikeys.sqlite3
    1 keys into database:
    [Id]    >> [Keyname]            >> [Secret]
    1       >> developers           >> ckFsWU5scVNXRjVZc3lJUmpIVzU=

On the OpenSSH machine, add users to ``/etc/yubimap``::

    $ cat /etc/yubimap
    barack:ibibhdhvhdhbhthb
    george:ibhdhehrhkhuifhv

Configure PAM to use YubiKey authentication (take care of API ``id`` and API
``key`` values)::

    $ head /etc/pam.d/sshd | grep include
    #@include common-auth
    @include yubi-auth
    
    $ cat /etc/pam.d/yubi-auth
    auth       required     pam_yubico.so authfile=/etc/yubimap id=1 key=ckFsWU5scVNXRjVZc3lJUmpIVzU= url=http://yubikeyval.local:8000/wsapi/2.0/verify?id=%d&otp=%s mode=client token_id_length=16

Configure OpenSSH::

    $ tail -4 /etc/ssh/sshd_config
    ChallengeResponseAuthentication  no
    Match User george,barack
        PasswordAuthentication       yes
        AuthenticationMethods        publickey,password


TODO
====

OATH/HOTP is not supported at present.


Original author
===============

 * Alessio Periloso <mail *at* periloso.it>
