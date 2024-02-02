from dataclasses import dataclass
from pathlib import Path
import plistlib
from flattenipsw.exception import InvalidBuildManfest

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
    except KeyError:
        raise InvalidBuildManfest(path=build_manifest, key="BuildIdentities[0].Manifest.OS.Info.Path")

    dmg_path = DmgPath(filesystem=fs_path)
    
    try:
        dyld_shared_cache = manifest["BuildIdentities"][0]["Manifest"]["Cryptex1,SystemOS"]["Info"]["Path"]
        dmg_path.dyld_shared_cache = ipsw_extract / dyld_shared_cache
    except (KeyError, TypeError):
        dyld_shared_cache = None
        
    return dmg_path