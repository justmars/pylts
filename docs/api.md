# Litestream AWS API

This requires an instantiated [configuration][configuration]:

```py
from pylts import ConfigS3

try:
    stream = ConfigS3() # uses .env and default folder/db
except ValidationError as e:
    raise Exception(f"Missing fields; see {e=}")
```

## Restore

Download the database in `@dbpath` from the replica url `s3://`

```py
>>> stream.restore() # equivalent to litestream restore ...
```

## Delete

Delete the database in the folder specified.

```py
>>> stream.delete() # used prior to restoration
```

## Replicate

Upload the database in `@dbpath` to replica url `s3://`

```py
>>> stream.replicate() # equivalent to litestream replicate ...
```
