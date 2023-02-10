import subprocess
from pathlib import Path

import click
from loguru import logger
from pydantic import BaseSettings, Field, ValidationError


class AmazonS3(BaseSettings):
    key: str = Field(
        default=...,
        repr=False,
        title="Bucket Access Key ID",
        env="LITESTREAM_ACCESS_KEY_ID",
    )
    token: str = Field(
        default=...,
        repr=False,
        title="Bucket Secret Key Token",
        env="LITESTREAM_SECRET_ACCESS_KEY",
    )
    s3: str = Field(
        default=...,
        repr=True,
        title="Replica URL",
        description="Should be in the format: s3://bucket/pathname",
        env="REPLICA_URL",
        regex=r"^s3:\/\/.*$",
        max_length=100,
    )
    db: str = Field(
        default="db.sqlite",
        title="Database Path",
        description="Where the database will reside in the client.",
        env="DB_SQLITE",
        regex=r"^[a-z]{1,20}.*\.(sqlite|db)$",
        max_length=50,
    )

    class Config:
        env_file = ".env"
        env_file_encoding = "utf-8"

    @property
    def dbpath(self) -> Path:
        folder = Path(__file__).parent.parent / "data"
        folder.mkdir(exist_ok=True)
        return folder / self.db

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


try:
    lts = AmazonS3()
except ValidationError as e:
    raise Exception(f"Missing fields; see {e=}")


@click.command()
def aws_restore_db():
    """Wrapper around litestream to download a copy of the database from a
    preconfigured bucket in AWS. This assumes secrets have been previously set.
    """
    lts.delete()
    lts.restore()


@click.command()
def aws_replicate_db():
    """Wrapper around litestream to create a copy of the database to a
    preconfigured bucket in AWS. This assumes secrets have been previously set.
    """
    lts.replicate()


@click.group()
def group():
    pass


group.add_command(aws_restore_db)
group.add_command(aws_replicate_db)
