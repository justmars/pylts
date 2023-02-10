import click

from .aws import litestream


@click.command()
def aws_restore_db():
    """Wrapper around litestream to download a copy of the database from a
    preconfigured bucket in AWS. This assumes secrets have been previously set.
    """
    litestream.delete()
    litestream.restore()


@click.command()
def aws_replicate_db():
    """Wrapper around litestream to create a copy of the database to a
    preconfigured bucket in AWS. This assumes secrets have been previously set.
    """
    litestream.replicate()


@click.group()
def group():
    pass


group.add_command(aws_restore_db)
group.add_command(aws_replicate_db)
