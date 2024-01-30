from pathlib import Path
import pytest
from src.flatten import NotAnIPSW, ipsw_unzip
import shutil


@pytest.fixture
def ipsw() -> Path:
    return Path(__file__).parent / 'resources' / 'ios13.ipsw'

@pytest.fixture
def not_an_ipsw() -> Path:
    return Path(__file__).parent / 'resources' / 'not_a_zip.txt'

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
