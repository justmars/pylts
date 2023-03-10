# syntax=docker/dockerfile:1.2
FROM python:3.11.2-slim-buster

ARG LITESTREAM_VER=0.3.9 \
  SQLITE_YEAR=2023 \
  SQLITE_VER=3410000

ENV PYTHONDONTWRITEBYTECODE=1 \
  PYTHONUNBUFFERED=1 \
  LD_LIBRARY_PATH=/usr/local/lib

RUN apt update \
  && apt install -y build-essential wget pkg-config \
  && apt clean

ADD https://github.com/benbjohnson/litestream/releases/download/v$LITESTREAM_VER/litestream-v$LITESTREAM_VER-linux-amd64-static.tar.gz /tmp/litestream.tar.gz
RUN tar -C /usr/local/bin -xzf /tmp/litestream.tar.gz \
  && rm /tmp/litestream.tar.gz

RUN wget "https://www.sqlite.org/$SQLITE_YEAR/sqlite-autoconf-$SQLITE_VER.tar.gz" \
  && tar xzf sqlite-autoconf-$SQLITE_VER.tar.gz \
  && cd sqlite-autoconf-$SQLITE_VER \
  && ./configure --disable-static --enable-fts5 --enable-json1 CFLAGS="-g -O2 -DSQLITE_ENABLE_JSON1" \
  && make && make install \
  && cd .. \
  && rm -rf sqlite-autoconf-$SQLITE_VER \
  && rm sqlite-autoconf-$SQLITE_VER.tar.gz

# Start app
COPY requirements.txt requirements.txt
COPY pylts /pylts
RUN pip3 install -U pip && pip3 install -r requirements.txt
CMD ["python", "-m", "pylts", "aws-restore-db"]
