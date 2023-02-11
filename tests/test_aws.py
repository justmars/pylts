from pathlib import Path

import pytest

from pylts.aws import ConfigS3


@pytest.fixture()
def aws_litestream():
    return ConfigS3(key="key", token="token", s3="s3://test/db")


@pytest.fixture()
def data_folder():
    return Path(__file__).parent.parent / "data"


def test_aws(aws_litestream, data_folder):
    assert aws_litestream.dbpath.parent == data_folder
