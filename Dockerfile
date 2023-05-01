# syntax=docker/dockerfile:1.2
FROM python:3.11-slim-bullseye
ENV PYTHONUNBUFFERED=1 \
    PYTHONDONTWRITEBYTECODE=1 \
    PIP_DISABLE_PIP_VERSION_CHECK=1

RUN apt update \
  && apt install -y build-essential wget pkg-config \
  && apt clean

ARG litestream_ver=0.3.9
ADD https://github.com/benbjohnson/litestream/releases/download/v$litestream_ver/litestream-v$litestream_ver-linux-amd64-static.tar.gz /tmp/litestream.tar.gz
RUN tar -C /usr/local/bin -xzf /tmp/litestream.tar.gz && rm /tmp/litestream.tar.gz

ARG sqlite_year=2023
ARG sqlite_ver=3410200
RUN wget "https://www.sqlite.org/$sqlite_year/sqlite-autoconf-$sqlite_ver.tar.gz" \
  && tar xzf sqlite-autoconf-$sqlite_ver.tar.gz \
  && rm sqlite-autoconf-$sqlite_ver.tar.gz \
  && cd sqlite-autoconf-$sqlite_ver \
  && ./configure --disable-static --enable-fts5 --enable-json1 CFLAGS="-g -O2 -DSQLITE_ENABLE_JSON1" \
  && make && make install

# Start app
COPY pylts /pylts
RUN pip install -r /pylts/requirements.txt
CMD ["python", "-m", "pylts", "aws-restore-db"]
