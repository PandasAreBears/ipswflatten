from pathlib import Path
from typing import Generator
import pytest
from flattenipsw.flatten import NotAnIPSW, ipsw_unzip
from flattenipsw.extract import ipsw_build_dmg_path, DmgPath
from flattenipsw.extract import ipsw_mount_dmg_context, ipsw_mount_dmg, ipsw_unmount_dmg
import shutil


@pytest.fixture
def ipsw_ios13() -> Path:
    return Path(__file__).parent / 'resources' / 'ipsw' / 'ios13.ipsw'

@pytest.fixture
def ipsw_ios16() -> Path:
    return Path(__file__).parent / 'resources' / 'ipsw' / 'ios16.ipsw'

@pytest.fixture
def not_an_ipsw() -> Path:
    return Path(__file__).parent / 'resources' / 'not_a_zip.txt'

@pytest.fixture
def extracted_ipsw_ios13(ipsw_ios13: Path) -> Generator[Path, None, None]:
    out = ipsw_unzip(ipsw_ios13, None)
    assert out.exists()
    assert out.is_dir()

    yield out

    # cleanup
    shutil.rmtree(out)

@pytest.fixture
def extracted_ipsw_ios16(ipsw_ios16: Path) -> Generator[Path, None, None]:
    out = ipsw_unzip(ipsw_ios16, None)
    assert out.exists()
    assert out.is_dir()

    yield out

    # cleanup
    shutil.rmtree(out)

@pytest.fixture
def dmg_path_ios13(extracted_ipsw_ios13: Path) -> Generator[DmgPath, None, None]:
    paths = ipsw_build_dmg_path(extracted_ipsw_ios13)

    assert paths.filesystem.exists()
    assert paths.filesystem.is_file()

    assert paths.dyld_shared_cache is None 

    yield paths

@pytest.fixture
def dmg_path_ios16(extracted_ipsw_ios16: Path) -> Generator[DmgPath, None, None]:
    paths = ipsw_build_dmg_path(extracted_ipsw_ios16)

    assert paths.filesystem.exists()
    assert paths.filesystem.is_file()

    assert paths.dyld_shared_cache is not None
    assert paths.dyld_shared_cache.exists()
    assert paths.dyld_shared_cache.is_file()

    yield paths


def test_ipsw_unzips_zip_file(ipsw_ios13: Path) -> None:
    out = ipsw_unzip(ipsw_ios13, None)
    assert out.exists()
    assert out.is_dir()

    # cleanup   
    shutil.rmtree(out)

def test_ipsw_unzip_to_dir(ipsw_ios13: Path) -> None:
    out = ipsw_unzip(ipsw_ios13, Path('/tmp/ios13'))
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

def test_extract_dmg_paths_with_dyld_shared_cache(extracted_ipsw_ios16: Path) -> None:
    paths = ipsw_build_dmg_path(extracted_ipsw_ios16)
    assert paths.filesystem.exists()
    assert paths.filesystem.is_file()

    assert paths.dyld_shared_cache is not None
    assert paths.dyld_shared_cache.exists()
    assert paths.dyld_shared_cache.is_file()

def test_mount_dmg_no_mount_point(dmg_path_ios13: DmgPath) -> None:
    mount_point = ipsw_mount_dmg(dmg_path_ios13.filesystem, None)
    assert mount_point.exists()
    assert mount_point.is_dir()
    assert len(list(mount_point.glob("*"))) > 0

    # cleanup
    ipsw_unmount_dmg(mount_point)

def test_mount_dmg_with_mount_point(dmg_path_ios13: DmgPath) -> None:
    mount_path = Path('/tmp/ios13_mount')
    mount_path.mkdir(exist_ok=True)

    mount_point = ipsw_mount_dmg(dmg_path_ios13.filesystem, mount_path)
    assert mount_point == mount_path
    assert mount_point.exists()
    assert mount_point.is_dir()
    assert len(list(mount_point.glob("*"))) > 0

    # cleanup
    ipsw_unmount_dmg(mount_point)

def test_mount_dmg_context_manager(dmg_path_ios13: DmgPath) -> None:
    with ipsw_mount_dmg_context(dmg_path_ios13.filesystem) as mount_point:
        assert mount_point.exists()
        assert mount_point.is_dir()
        assert len(list(mount_point.glob("*"))) > 0

    assert not mount_point.exists()

def test_mount_dmg_context_manager_ios16(dmg_path_ios16: DmgPath) -> None:
    with ipsw_mount_dmg_context(dmg_path_ios16.filesystem) as mount_point:
        assert mount_point.exists()
        assert mount_point.is_dir()
        assert len(list(mount_point.glob("*"))) > 0

    assert not mount_point.exists()

    assert dmg_path_ios16.dyld_shared_cache is not None

    with ipsw_mount_dmg_context(dmg_path_ios16.dyld_shared_cache) as mount_point:
        assert mount_point.exists()
        assert mount_point.is_dir()
        assert len(list(mount_point.glob("*"))) > 0

    assert not mount_point.exists()