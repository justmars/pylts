"""
See sample setup to generate `click`-based commands
based on the secrets included in the .env file.
"""
import click
from pydantic import ValidationError

from .aws import ConfigS3

try:
    litestream = ConfigS3()
except ValidationError as e:
    raise Exception(f"Missing fields; see {e=}")


@click.command()
def aws_restore_db():
    """Wrapper around litestream to download a copy of the database from a
    preconfigured bucket in AWS. This assumes secrets have been previously set.
    Will now be usable as a CLI via `python -m pylts aws_restore_db` for this app.
    """
    litestream.delete()
    litestream.restore()


@click.command()
def aws_replicate_db():
    """Wrapper around litestream to create a copy of the database to a
    preconfigured bucket in AWS. This assumes secrets have been previously set.
    Will now be usable as a CLI via `python -m pylts aws_replicate_db` for this app.
    """
    litestream.replicate()


@click.group()
def group():
    pass


group.add_command(aws_restore_db)
group.add_command(aws_replicate_db)
