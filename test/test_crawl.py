
from pathlib import Path
import pytest
from flattenipsw.crawl import FileHandler, ipsw_crawl_filesystem
import shutil
import json


@pytest.fixture
def fake_fs():
    return Path(__file__).parent / 'resources' / 'fake_fs'


def test_fs_crawl_name_signature(fake_fs: Path) -> None:
    class TestHandler(FileHandler):
        file_name = "hi.py"

        def handle_file(self, file: Path, output: Path) -> list[str]:
            shutil.copy(file, output / file.name)

            return [file.name]

    handler = TestHandler()
        
    output = ipsw_crawl_filesystem(mount_point=fake_fs, file_handlers=[handler])

    assert output.exists()
    assert output.is_dir()
    assert (output / "hi.py").exists()
    assert not (output /"hi.c").exists()
    assert not (output /"hi.txt").exists()

    # cleanup
    shutil.rmtree(output)
        

def test_fs_crawl_type_signature(fake_fs: Path) -> None:
    class TestHandler(FileHandler):
        file_type = "Python script"

        def handle_file(self, file: Path, output: Path) -> list[str]:
            shutil.copy(file, output / file.name)

            return [file.name]

    handler = TestHandler()
        
    output = ipsw_crawl_filesystem(mount_point=fake_fs, file_handlers=[handler])

    assert output.exists()
    assert output.is_dir()
    assert (output / "hi.py").exists()
    assert not (output /"hi.c").exists()
    assert not (output /"hi.txt").exists()

    # cleanup
    shutil.rmtree(output)


def test_locations_json_is_correct(fake_fs: Path) -> None:
    class TestHandler(FileHandler):
        file_type = "Python script"

        def handle_file(self, file: Path, output: Path) -> list[str]:
            shutil.copy(file, output / file.name)

            return [file.name]

    handler = TestHandler()
        
    output = ipsw_crawl_filesystem(mount_point=fake_fs, file_handlers=[handler])

    locations_file = output / "locations.json"
    assert locations_file.exists()

    with open(locations_file) as f:
        locations = json.load(f)
        assert locations == {"hi.py": "hi.py"}

    