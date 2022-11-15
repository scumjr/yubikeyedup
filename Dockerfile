FROM python:alpine

RUN apk update \
    && apk add \
        git \
        gcc \
        g++ \
        pcsc-lite-dev \
        openssl \
        openssl-dev \
        pkgconfig

RUN pip3 install \
        pycryptodome \
        pycryptodomex

WORKDIR /src

COPY . /src

ENTRYPOINT [ "./src/yubiserve.py" ]
CMD [ "--db", "/db/yubikeys.sqlite3" ]
