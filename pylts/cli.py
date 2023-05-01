import click
from pydantic import ValidationError

from .aws import ConfigS3

try:
    """
    See sample setup to generate `click`-based commands
    based on the secrets included in the .env file.
    """
    litestream = ConfigS3()
except ValidationError as e:
    raise Exception(f"Missing fields; see {e=}")


@click.command()
def aws_restore_db():
    """Wrapper around litestream to download a copy of the database from a
    preconfigured bucket in AWS. This assumes secrets have been previously set.
    Will now be usable as a CLI via `python -m pylts aws-restore-db` for this app.

    If done in the terminal, the command will run but still need to do
    `export LITESTREAM_ACCESS_KEY_ID=xxx` and `export LITESTREAM_SECRET_ACCESS_KEY=yyy`
    since `litestream = ConfigS3()` is only a wrapper to construct the actual
    `litestream` command.
    """
    litestream.delete()
    litestream.restore()


@click.command()
@click.argument("seconds")
def aws_replicate_db(seconds):
    """Wrapper around litestream to upload a copy of the database to a
    preconfigured bucket in AWS. This assumes secrets have been previously set.
    Will now be usable as a CLI via `python -m pylts aws-replicate-db` for this app.

    If done in the terminal, the command will run but still need to do
    `export LITESTREAM_ACCESS_KEY_ID=xxx` and `export LITESTREAM_SECRET_ACCESS_KEY=yyy`
    since `litestream = ConfigS3()` is only a wrapper to construct the actual
    `litestream` command.
    """
    litestream.timed_replicate(timeout_seconds=int(seconds))


@click.group()
def group():
    pass


group.add_command(aws_restore_db)
group.add_command(aws_replicate_db)
