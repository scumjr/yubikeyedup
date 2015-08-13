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


TODO
====

OATH/HOTP is not supported at present.


Original author
===============

 * Alessio Periloso <mail *at* periloso.it>
