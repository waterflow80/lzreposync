import pytest
from implementation_1 import create_args_parser, download_and_parse_metadata


def test_no_arguments():
    parser = create_args_parser()
    with pytest.raises(ValueError, match="Target url was not provided."):
        args = parser.parse_args([])
        download_and_parse_metadata(args)


@pytest.mark.skip
def test_url_argument(capsys):
    parser = create_args_parser()
    args = parser.parse_args(['-u', 'https://download.opensuse.org/update/leap/15.5/oss/repodata/'])
    download_and_parse_metadata(args)
    captured = capsys.readouterr()
    assert captured.out == 'https://download.opensuse.org/update/leap/15.5/oss/repodata/'
