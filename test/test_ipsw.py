from pathlib import Path
import pytest
from flattenipsw.flatten import NotAnIPSW, ipsw_unzip
from flattenipsw.extract import ipsw_build_dmg_path
import shutil


@pytest.fixture
def ipsw() -> Path:
    return Path(__file__).parent / 'resources' / 'ios13.ipsw'

@pytest.fixture
def not_an_ipsw() -> Path:
    return Path(__file__).parent / 'resources' / 'not_a_zip.txt'

@pytest.fixture
def extracted_ipsw_ios13(ipsw: Path) -> Path:
    out = ipsw_unzip(ipsw, None)
    assert out.exists()
    assert out.is_dir()

    yield out

    # cleanup
    shutil.rmtree(out)


def test_ipsw_unzips_zip_file(ipsw: Path) -> None:
    out = ipsw_unzip(ipsw, None)
    assert out.exists()
    assert out.is_dir()

    # cleanup   
    shutil.rmtree(out)

def test_ipsw_unzip_to_dir(ipsw: Path) -> None:
    out = ipsw_unzip(ipsw, Path('/tmp/ios13'))
    assert out.exists()
    assert out.is_dir()

    # cleanup
    shutil.rmtree(out)

def test_ipsw_doesnt_unzip_non_zip_file(not_an_ipsw: Path) -> None:
    with pytest.raises(NotAnIPSW):
        ipsw_unzip(not_an_ipsw, None)

def test_extract_dmg_paths(extracted_ipsw_ios13: Path) -> None:
    paths = ipsw_build_dmg_path(extracted_ipsw_ios13)
    assert paths.filesystem.exists()
    assert paths.filesystem.is_file()
    assert paths.dyld_shared_cache is None