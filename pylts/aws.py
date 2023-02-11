import subprocess
from pathlib import Path

from loguru import logger
from pydantic import BaseSettings, Field


class ConfigS3(BaseSettings):
    """Generate a configuration instance to determine how to access the _replica url_ and
    where to place the _local db_ from such url.

    ## Replica url

    Follow [instructions](https://litestream.io/guides/s3/) to get:

    Field | Type | Description | Declare in .env
    --:|:--:|:--|:--
    key | str | Access Key | `LITESTREAM_ACCESS_KEY_ID`
    token | str | Secret Token | `LITESTREAM_SECRET_ACCESS_KEY`
    s3 | str | e.g. `s3://<bucket_name>/>/<folder>` | `REPLICA_URL`

    ## Local db

    There are two fields that can be declared affecting the local database path

    Field | Type | Description
    --:|:--:|:-
    `db` | str | Optional, Default: _db.sqlite_. Must end in .db or .sqlite
    `folder` | pathlib.Path | Default: root folder based on Path(__file__). Where to place the `db`

    The `@dbpath` is based on `folder` / `db`.

    Examples:
        >>> from pylts import ConfigS3
        >>> from pathlib import Path
        >>> stream = ConfigS3(key="xxx", token="yyy", s3="s3://x/x.db", folder=Path().cwd() / "data")
        >>> stream
        ConfigS3(s3='s3://x/x.db', db='db.sqlite')
        >>> stream.dbpath.name
        'db.sqlite'
        >>> stream.dbpath.parent.stem
        'data'
        >>> stream.dbpath.parent.parent.stem
        'pylts'
    """  # noqa: E501

    key: str = Field(
        default=...,
        repr=False,
        title="AWS Access Key ID",
        env="LITESTREAM_ACCESS_KEY_ID",
    )
    token: str = Field(
        default=...,
        repr=False,
        title="AWS Secret Key",
        env="LITESTREAM_SECRET_ACCESS_KEY",
    )
    s3: str = Field(
        default=...,
        repr=True,
        title="s3 URL",
        description="Should be in the format: s3://bucket/pathname",
        env="REPLICA_URL",
        regex=r"^s3:\/\/.*$",
        max_length=100,
    )
    folder: Path = Field(
        default=Path(__file__).parent.parent / "data",
        repr=False,
        title="Folder",
        description="Should be folder in the root's /data path",
    )
    db: str = Field(
        default="db.sqlite",
        title="Database File",
        description="Where db will reside in client.",
        env="DB_SQLITE",
        regex=r"^[a-z]{1,20}.*\.(sqlite|db)$",
        max_length=50,
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def dbpath(self) -> Path:
        self.folder.mkdir(exist_ok=True)
        return self.folder / self.db

    def delete(self):
        logger.warning(f"Deleting {self.dbpath=}")
        self.dbpath.unlink(missing_ok=True)

    def run(self, run_args: list[str]) -> Path:
        cmd = {" ".join(run_args)}
        logger.info(f"Run: {cmd}")
        logger.debug(subprocess.run(run_args, capture_output=True))
        return self.dbpath

    def restore(self) -> Path:
        return self.run(
            run_args=[
                "litestream",
                "restore",
                "-v",  # verbose
                "-o",  # output
                f"{str(self.dbpath)}",  # output path
                self.s3,  # source of restore
            ],
        )

    def replicate(self) -> Path:
        return self.run(
            run_args=[
                "litestream",
                "replicate",
                str(self.dbpath),  # path to loca
                self.s3,  # where to replicate
            ]
        )
