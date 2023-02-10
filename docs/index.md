# pylts Docs

Limited pydantic wrapper over [litestream](https://litestream.io/) so that AWS litestream commands can be used as a subprocess of python scripts.

## Create an AWS bucket

Follow [instructions](https://litestream.io/guides/s3/) to get:

1. S3 Key ID
2. S3 Secret Key
3. S3 Replica URL

## Set secrets

Secrets must be set in an `.env` file:

Secret | Description
--:|:--
LITESTREAM_ACCESS_KEY_ID | See how this is generated in chosen bucket
LITESTREAM_SECRET_ACCESS_KEY | See how this is generated in chosen bucket
REPLICA_URL | Where to get the replica for restoration and replication, e.g. in aws: `s3://<bucket_name>/><folder>`
DB_SQLITE | Optional, if not set _db.sqlite_, will be placed in a `/data/db.sqlite`

### .venv

```sh
poetry add pylts # install
poetry shell # enter shell / virtual environment to set up secrets in local dev
export LITESTREAM_ACCESS_KEY_ID=xxx
export LITESTREAM_SECRET_ACCESS_KEY=yyy
export REPLICA_URL=s3://x/x.db
```

## Commands

### Restore

```sh
# set secrets first
python -m pylts aws-restore-db
```

### Replicate

```sh
# set secrets first
python -m pylts aws-replicate-db
```

## Dockerfile

Elements | Version | Version List
--:|:--|--:
python | `3.11.1` | [versions](https://www.python.org/downloads/)
litestream | `0.3.9` | [versions](https://github.com/benbjohnson/litestream/releases)
sqlite | `3.40.1` | [versions](https://www.sqlite.org/download.html)

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
