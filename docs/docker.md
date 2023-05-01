# Dockerfile Sample

```dockerfile title="Annotated sample file"
# syntax=docker/dockerfile:1.2

# (1)
FROM python:3.11-slim-bullseye

ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

# (2)
RUN apt update && apt install -y build-essential wget pkg-config && apt clean

# (3)
ARG litestream_ver=0.3.9
ADD https://github.com/benbjohnson/litestream/releases/download/v$litestream_ver/litestream-v$litestream_ver-linux-amd64-static.tar.gz /tmp/litestream.tar.gz
RUN tar -C /usr/local/bin -xzf /tmp/litestream.tar.gz && rm /tmp/litestream.tar.gz

# (4)
ARG sqlite_year=2023
ARG sqlite_ver=3410200
RUN wget "https://www.sqlite.org/$sqlite_year/sqlite-autoconf-$sqlite_ver.tar.gz" \
  && tar xzf sqlite-autoconf-$sqlite_ver.tar.gz \
  && rm sqlite-autoconf-$sqlite_ver.tar.gz \
  && cd sqlite-autoconf-$sqlite_ver \
  && ./configure --disable-static --enable-fts5 --enable-json1 CFLAGS="-g -O2 -DSQLITE_ENABLE_JSON1" \
  && make && make install

# (5)
COPY code /code
RUN pip install -r /pylts/requirements.txt
CMD ["python", "-m", "pylts", "aws-restore-db"]
```

1. Review python [version](https://www.python.org/downloads/)
2. Get preliminary tools to process litestream and sqlite
3. Review litestream [version](https://github.com/benbjohnson/litestream/releases)
4. The version that comes with python isn't the most updated sqlite version, hence need to compile the latest one and
configure with extensions. Review [year and version](https://www.sqlite.org/download.html)
5. Assuming code found in top-level directory `/code` (from the docker build context), ensure `requirements.txt` found in hypothetical `/code`

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
