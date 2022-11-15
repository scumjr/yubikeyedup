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

run: _stop
    docker run \
        --detach \
        --name {{ tool }} \
        --rm \
        -it \
        -v $(realpath {{ database }}):/db/yubikeys.sqlite3 \
        -v /run/pcscd/pcscd.comm:/run/pcscd/pcscd.comm \
        -p 8000:8000 \
        {{ tool }}

test: run
    #!/bin/bash
    nonce=$(echo -n $RANDOM | sha256sum | head -c 16 | cut -d ' ' -f1)
    echo -n "Yubikey token: " 
    read -s token && echo
    echo
    curl "localhost:8000/wsapi/2.0/verify?id=1&nonce=$nonce&otp=$token"

_stop:
    docker stop {{ tool }} || true
