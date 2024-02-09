
from pathlib import Path
import tempfile
import pytest
from flattenipsw.crawl import FileRule, ipsw_crawl_filesystem


@pytest.fixture
def fake_fs():
    return Path(__file__).parent / 'resources' / 'fake_fs'


def test_fs_crawl_name_signature(fake_fs: Path) -> None:
    class TestHandler(FileRule):
        file_name = "hi.py"

    with tempfile.TemporaryDirectory() as tempdir:
        output = Path(tempdir)
        locations = ipsw_crawl_filesystem(mount_point=fake_fs, rule=TestHandler(), output=output)

        assert len(locations) == 1

        assert (output / "hi.py").exists()
        assert not (output /"hi.c").exists()
        assert not (output /"hi.txt").exists()

        

def test_fs_crawl_type_signature(fake_fs: Path) -> None:
    class TestHandler(FileRule):
        file_type = "Python script"

    with tempfile.TemporaryDirectory() as tempdir:
        output = Path(tempdir)
        locations = ipsw_crawl_filesystem(mount_point=fake_fs, rule=TestHandler(), output=output)

        assert len(locations) == 1

        assert (output / "hi.py").exists()
        assert not (output /"hi.c").exists()
        assert not (output /"hi.txt").exists()


def test_fs_crawl_name_and_type_signature(fake_fs: Path) -> None:
    class TestHandler(FileRule):
        file_name = "hi.py"
        file_type = "Python script"

    with tempfile.TemporaryDirectory() as tempdir:
        output = Path(tempdir)
        locations = ipsw_crawl_filesystem(mount_point=fake_fs, rule=TestHandler(), output=output)

        assert len(locations) == 1

        assert (output / "hi.py").exists()
        assert not (output /"hi.c").exists()
        assert not (output /"hi.txt").exists()


def test_fs_crawl_matches_none(fake_fs: Path) -> None:
    class TestHandler(FileRule):
        file_name = "hi.c"
        file_type = "Python script"

    with tempfile.TemporaryDirectory() as tempdir:
        output = Path(tempdir)
        locations = ipsw_crawl_filesystem(mount_point=fake_fs, rule=TestHandler(), output=output)

        assert len(locations) == 0

        assert not (output / "hi.py").exists()
        assert not (output /"hi.c").exists()
        assert not (output /"hi.txt").exists()