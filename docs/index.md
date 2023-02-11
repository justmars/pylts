# pylts Docs

A thin, reusable [pydantic](https://docs.pydantic.dev) wrapper over [litestream](https://litestream.io/)
applied specifically to an AWS bucket.

This makes it easier to use / model litestream inside a python script.

It works by adding relevant fields to an `.env` file that are associated with an AWS bucket for
restoration and replication.

## Configuration

::: pylts.aws.ConfigS3
