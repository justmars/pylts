# Dockerfile Sample

Elements | Version | Version List
--:|:--|--:
python | `3.11.1` | [versions](https://www.python.org/downloads/)
litestream | `0.3.9` | [versions](https://github.com/benbjohnson/litestream/releases)
sqlite | `3.40.1` | [versions](https://www.sqlite.org/download.html)

## Base

Get preliminary tools to process litestream and sqlite

```dockerfile
RUN apt update && apt install -y build-essential wget pkg-config git && apt clean
```

## Litestream

```dockerfile
ARG LITESTREAM_VER=0.3.9
ADD https://github.com/benbjohnson/litestream/releases/download/v$LITESTREAM_VER/litestream-v$LITESTREAM_VER-linux-amd64-static.tar.gz /tmp/litestream.tar.gz
RUN tar -C /usr/local/bin -xzf /tmp/litestream.tar.gz
```

Review the latest version to get the updated release from github.

## sqlite

The version that comes with python isn't the most updated sqlite version, hence need to compile the latest one and
configure with extensions:

```dockerfile
ARG SQLITE_YEAR=2022
ARG SQLITE_VER=3400100
RUN wget "https://www.sqlite.org/$SQLITE_YEAR/sqlite-autoconf-$SQLITE_VER.tar.gz" \
  && tar xzf sqlite-autoconf-$SQLITE_VER.tar.gz \
  && cd sqlite-autoconf-$SQLITE_VER \
  && ./configure --disable-static --enable-fts5 --enable-json1 CFLAGS="-g -O2 -DSQLITE_ENABLE_JSON1" \
  && make && make install
```

## Build / Run Sample

```sh
export LITESTREAM_ACCESS_KEY_ID=xxx
export LITESTREAM_SECRET_ACCESS_KEY=yyy
export REPLICA_URL=s3://x/x.db
poetry export -f requirements.txt -o requirements.txt --without-hashes
docker build .
docker run it \
  -e LITESTREAM_ACCESS_KEY_ID \
  -e LITESTREAM_SECRET_ACCESS_KEY \
  -e REPLICA_URL
```
