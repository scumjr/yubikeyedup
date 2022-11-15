set shell := ["bash", "-c"]

_default:
    @just --list

database := "yubikeys.sqlite3"

_setup:
    [ ! -f {{ database }} ] && ./tools/dbcreate.py {{ database }} || true

add_key name:
    ./tools/flash.py {{ name }} {{ database }}

@serve:
    ./src/yubiserve.py --db {{ database }}
