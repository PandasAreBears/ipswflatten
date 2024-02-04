from contextlib import contextmanager
from dataclasses import dataclass
from pathlib import Path
import plistlib
import tempfile
from typing import Generator
from flattenipsw.exception import InvalidBuildManfest
import subprocess
import logging

logger = logging.getLogger(__name__)

BUILD_MANIFEST = "BuildManifest.plist"

@dataclass
class DmgPath:
    filesystem: Path
    dyld_shared_cache: Path | None = None



def ipsw_build_dmg_path(ipsw_extract: Path) -> DmgPath:
    """Extract the filesystem and dyld_shared_cache paths from an IPSW extract.
    
    Args:
        ipsw_extract: The path to the extracted IPSW.
        
    Returns:
        The filesystem and dyld_shared_cache paths.
    """
    build_manifest = ipsw_extract / BUILD_MANIFEST
    if not build_manifest.exists():
        raise FileNotFoundError(build_manifest)
    
    with build_manifest.open('rb') as f:
        manifest = plistlib.load(f)
        
    try:
        filesystem = manifest["BuildIdentities"][0]["Manifest"]["OS"]["Info"]["Path"]
        fs_path = ipsw_extract / filesystem
        logger.info(f"Found filesystem dmg at {fs_path}")
    except KeyError:
        raise InvalidBuildManfest(path=build_manifest, key="BuildIdentities[0].Manifest.OS.Info.Path")

    dmg_path = DmgPath(filesystem=fs_path)
    
    try:
        dyld_shared_cache = manifest["BuildIdentities"][0]["Manifest"]["Cryptex1,SystemOS"]["Info"]["Path"]
        dmg_path.dyld_shared_cache = ipsw_extract / dyld_shared_cache
        logger.info(f"Found dyld shared cache dmg at {fs_path}")
    except (KeyError, TypeError):
        dyld_shared_cache = None
        
    return dmg_path


@contextmanager
def ipsw_mount_dmg_context(dmg_path: Path, mount_point: Path | None = None) -> Generator[Path, None, None]:
    """Mount a DMG file and yield the mount point.
    
    Args:
        dmg_path: The path to the DMG file.
        mount_point: The path to the mount point. If None, a temporary directory will be created.
        
    Yields:
        The path to the mount point.

    Raises:
        subprocess.CalledProcessError: If the apfs-fuse or fusermount command fails.
    """
    yield (mount_point := ipsw_mount_dmg(dmg_path, mount_point))

    ipsw_unmount_dmg(mount_point)

def ipsw_mount_dmg(dmg_path: Path, mount_point: Path | None = None) -> Path:
    """Mount a DMG file and return the mount point.
    
    Args:
        dmg_path: The path to the DMG file.
        mount_point: The path to the mount point. If None, a temporary directory will be created.
        
    Returns:
        The path to the mount point.

    Raises:
        subprocess.CalledProcessError: If the apfs-fuse command fails.
    """
    if mount_point is None:
        mount_point = Path(tempfile.mkdtemp())

    command = f"apfs-fuse -o uid=$UID {dmg_path} {mount_point}"
    subprocess.run(command, shell=True, check=True)
    logging.info(f"Mounted {dmg_path} at {mount_point}")

    return mount_point

def ipsw_unmount_dmg(mount_point: Path) -> None:
    """Unmount a DMG file.
    
    Args:
        mount_point: The path to the mount point.

    Raises:
        subprocess.CalledProcessError: If the fusermount command fails.
    """
    command = f"fusermount -u {mount_point}"
    subprocess.run(command, shell=True, check=True)
    mount_point.rmdir()
    logging.info(f"Unmounted {mount_point}")
