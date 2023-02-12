import datetime
import subprocess
from pathlib import Path
from subprocess import PIPE, CompletedProcess, Popen, TimeoutExpired

from loguru import logger
from pydantic import BaseSettings, Field


class ConfigS3(BaseSettings):
    """
    # ConfigS3

    ## Flow

    1. Add fields from s3 bucket to `.env`
    2. `.env` picked up by Pydantic `BaseSettings` model `ConfigS3`
    3. Python subprocesses to litestream replicate/restore will based on `ConfigS3`

    ## .env

    The necessary fields to declare in `.env` are:

    1. `LITESTREAM_ACCESS_KEY_ID`,
    2. `LITESTREAM_SECRET_ACCESS_KEY`
    3. `REPLICA_URL`.

    ## Replica URL

    The _replica url_ is the s3 bucket that will host the sqlite database,
    i.e. the db will be replicated here or the db will be restored from here.

    For AWS, the replica url is formatted likeso: `s3://<bucket_name>/<path>`.

    To create the bucket, follow [litestream instructions](https://litestream.io/guides/s3/).
    This results in some values that we can use to create the `ConfigS3` instance:

    Field | Type | Description | Declare in .env
    --:|:--:|:--|:--
    key | str | Access Key | `LITESTREAM_ACCESS_KEY_ID`
    token | str | Secret Token | `LITESTREAM_SECRET_ACCESS_KEY`
    s3 | str | Bucket URL | `REPLICA_URL`

    Note that these values can/should be declared in the `.env` file:

    ```sh
    # contents of .env
    LITESTREAM_ACCESS_KEY_ID=xxx
    LITESTREAM_SECRET_ACCESS_KEY=yyy
    REPLICA_URL=s3://zzz/db
    ```

    The configuration ensures that we can create a subprocess that is authorized
    to perform actions with the _replica url_.

    ## Local db

    The subprocesses involve a path to the database.

    There are two fields that can be declared in the configuration that can affect
    this path:

    Field | Type | Description
    --:|:--:|:-
    `db` | str | Optional, Default: _db.sqlite_. Must end in .db or .sqlite
    `folder` | pathlib.Path | Default: root folder based on Path(__file__). Where to place the `db`

    The `@dbpath` is based on `folder` / `db`.

    Examples:
        >>> from pylts import ConfigS3
        >>> from pathlib import Path
        >>> # The key, token, s3 are usually just set up in an .env file. They're included here for testing purposes. The folder however is advised to be explicitly declared
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
        """Examples:
            >>> from pylts import ConfigS3
            >>> from pathlib import Path
            >>> # The key, token, s3 are usually just set up in an .env file. They're included here for testing purposes. The folder however is advised to be explicitly declared
            >>> stream = ConfigS3(key="xxx", token="yyy", s3="s3://x/x.db", folder=Path().cwd() / "data")
            >>> stream.dbpath == Path().cwd() / "data" / "db.sqlite" # Automatic construction of default db name
            True

        Returns:
            Path: Where the database will be located locally.
        """  # noqa: E501
        self.folder.mkdir(exist_ok=True)
        return self.folder / self.db

    @property
    def replicate_args(self) -> list[str]:
        """When used in the command line `litestream replicate <dbpath> <replica_url>`
        works. As a subprocess, we itemize each item for future use.

        Examples:
            >>> from pylts import ConfigS3
            >>> from pathlib import Path
            >>> # The key, token, s3 are usually just set up in an .env file. They're included here for testing purposes. The folder however is advised to be explicitly declared
            >>> stream = ConfigS3(key="xxx", token="yyy", s3="s3://x/x.db", folder=Path().cwd() / "data")
            >>> args = stream.replicate_args
            >>> isinstance(stream.replicate_args, list)
            True
            >>> args[0] == "litestream"
            True
            >>> args[1] == "replicate"
            True
            >>> args[2] == str(stream.dbpath)
            True
            >>> args[3] == stream.s3
            True
        """  # noqa: E501
        return [
            "litestream",
            "replicate",
            str(self.dbpath),  # path to loca
            self.s3,  # where to replicate
        ]

    @property
    def restore_args(self) -> list[str]:
        """When used in the command line `litestream restore -o <dbpath> <replica_url>`
        works. As a subprocess, we itemize each item for future use.

        Examples:
            >>> from pylts import ConfigS3
            >>> from pathlib import Path
            >>> # The key, token, s3 are usually just set up in an .env file. They're included here for testing purposes. The folder however is advised to be explicitly declared
            >>> stream = ConfigS3(key="xxx", token="yyy", s3="s3://x/x.db", folder=Path().cwd() / "data")
            >>> args = stream.restore_args
            >>> isinstance(stream.restore_args, list)
            True
            >>> args[0] == "litestream"
            True
            >>> args[1] == "restore"
            True
            >>> args[-2] == str(stream.dbpath)
            True
            >>> args[-1] == stream.s3
            True

        """  # noqa: E501
        return [
            "litestream",
            "restore",
            "-v",  # verbose
            "-o",  # output
            f"{str(self.dbpath)}",  # output path
            self.s3,  # source of restore
        ]

    def restore(self) -> Path:
        """Runs the pre-configured litestream command (`@restore_args`) to restore the
        database from the replica url to the constructed database path at `@dbpath`.
        No need to use a timeout here since after restoration, the command terminates.
        This is unlike `self.timed_replicate()` which is continuously executed even
        after replication.
        """
        cmd = {" ".join(self.restore_args)}
        logger.info(f"Run: {cmd}")
        proc: CompletedProcess = subprocess.run(
            self.restore_args, capture_output=True
        )
        for line in proc.stderr.splitlines():
            logger.debug(line)
        return self.dbpath

    def delete(self):
        """Deletes the file located at the constructed database path `@dbpath`.

        Examples:
            >>> from pylts import ConfigS3
            >>> from pathlib import Path
            >>> # The key, token, s3 are usually just set up in an .env file. They're included here for testing purposes. The folder however is advised to be explicitly declared
            >>> stream = ConfigS3(key="xxx", token="yyy", s3="s3://x/x.db", folder=Path().cwd() / "data")
            >>> stream.dbpath.exists()
            True
            >>> stream.delete()
            >>> stream.dbpath.exists()
            False

        """  # noqa: E501
        logger.warning(f"Deleting {self.dbpath=}")
        self.dbpath.unlink(missing_ok=True)

    def get_result_on_timeout(
        self, cmd: list[str], timeout: int
    ) -> tuple[str, str]:
        """Returns results of a long-running process defined by `cmd` after the
        expiration of the `timeout`. This is an adoption of the python sample [code](https://docs.python.org/3.11/library/subprocess.html#subprocess.Popen.communicate)
        re: `Popen.communicate()`

        Because of the expiration of the timeout is an error, it falls into the second half of the
        tuple of strings returned.
        """  # noqa: E501
        p = Popen(cmd, text=True, stdout=PIPE, stderr=PIPE)
        try:
            logger.info(f"Output: {cmd=}")
            return p.communicate(timeout=timeout)
        except TimeoutExpired:
            logger.info(f"Timed Out: {cmd=}")
            p.kill()
            return p.communicate()

    def timed_replicate(self, timeout_seconds: int) -> bool:
        """Replication from litestream is a continuous, non-terminating command,
        hence the need for `timed_replicate()` to ensure that we only
        replicate a single time.

        We enforce this rule by ensuring that the replication process performed
        by `@replicate_args` should becompleted within `timeout_seconds`. Whether or not
        a replication is done will determine the acts to be performed and the value of
        the resulting boolean.

        If replication is successful, a snapshot is written to the `s3` url and the
        local `@dbpath` can be (and is) deleted.

        Args:
            timeout_seconds (int): Number of seconds

        Returns:
            bool: Whether the replication was successful within `timeout_seconds`
        """
        logger.info(
            f"Replication to {self.s3=} start: {datetime.datetime.now()=}"
        )
        res = self.get_result_on_timeout(self.replicate_args, timeout_seconds)
        _, stderr_data = res[0], res[1]  # stderr because of timeout err
        for text in stderr_data.splitlines():
            if "snapshot written" in text:  # see litestream prompt
                logger.success(f"Snapshot on {datetime.datetime.now()=}")
                self.dbpath.unlink()  # delete the file after replication
                return True
        return False
