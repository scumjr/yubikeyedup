set shell := ["bash", "-c"]

_default:
    @just --list

tool := "yubikeyedup"

database := "yubikeys.sqlite3"

_setup:
    [ ! -f {{ database }} ] && ./tools/dbcreate.py {{ database }} || true

add_key name:
    ./tools/flash.py {{ name }} {{ database }}

@serve:
    ./src/yubiserve.py --db {{ database }}

build:
    docker build -t {{ tool }} .

run:
    docker run --rm -it --name {{ tool }} \
        -v $(realpath {{ database }}):/db/yubikeys.sqlite3 \
        -v /run/pcscd/pcscd.comm:/run/pcscd/pcscd.comm \
        -p 8000:8000 \
        {{ tool }}

