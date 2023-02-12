# pylts Docs

A thin, reusable [pydantic](https://docs.pydantic.dev) wrapper over _limited_ [litestream](https://litestream.io/) functions: makes it easier to use litestream inside a python script to handle the _replicate_ and _restore_ aspects of an sqlite database
in an s3 bucket.

## Usage

```py
# assumes installation via pip install pylts / poetry add pylts
>>> from pylts import ConfigS3 # inherits from pydantic.BaseSettings
>>> from pathlib import Path
>>> d = Path().cwd() / "data" # where to place database
>>> stream = ConfigS3(folder=d) # assumes .env variables based on <s3> bucket
>>> stream.dbpath # constructed local <db> path based on folder
>>> stream.s3 # replica s3:// url in aws <s3>
>>> stream.restore() # subprocess: 'litestream restore -o <db> <s3>'
>>> stream.timed_replicate() # subprocess: 'litestream replicate <db> <s3>'
```

## Flow

### Placement

```mermaid
---
title: From Local to Bucket to Production
---
flowchart LR
  subgraph fly.io
    volume
    app
  end
  subgraph aws
    s3(s3 bucket)--pylts restore volume-->app
  end
  subgraph local
    db--"litestream replicate (args)"-->s3
    code--fly deploy-->app
  end
```

Environment | Task
--:|:--
local | Set up _repo_ with a _sqlite.db_ (`db`)
local | With `pydantic`-parsed values, `litestream replicate` this created `db` to `s3`
local | Deploy the _repo_ to `fly.io`
prod | Pydantically restore `db` from `s3` to `fly.io`

### Retrieval

The database that is (re)stored in the volume (fly.io) may be updated either by cron jobs or by adding, deleting entries directly. How do we ensure these updates are persisted to the s3 bucket?

```mermaid
---
title: From Production to Bucket to Local
---
flowchart LR
  subgraph fly.io
    volume
    app
  end
  subgraph aws
    app--pylts replicate volume-->s3
  end
  subgraph local
    s3--"litestream restore (args)"-->db
    code
  end
```
