from contextlib import contextmanager
from pathlib import Path
from typing import Iterator, Optional
import zipfile
from flattenipsw.exception import NotAnIPSW

def ipsw_unzip(ipsw: Path, out: Optional[Path]) -> Path:
    """Unzip an IPSW file to a directory.

    Args:
        ipsw: The path to the IPSW file.
        out: The path to the output directory.

    Returns:    
        The path to the output directory.
    """
    if out is None:
        out = ipsw.parent / ipsw.stem

    out.mkdir(parents=True, exist_ok=True)

    with ipsw_open(ipsw=ipsw) as zf:

        zf.extractall(path=out)

    return out


@contextmanager
def ipsw_open(ipsw: Path) -> Iterator[zipfile.ZipFile]:
    """Open an IPSW file as a zipfile.

    Args:
        ipsw: The path to the IPSW file.

    Returns:
        The zipfile.

    Raises:
        NotAnIPSW: If the given file is not an IPSW.
    """
    try:
        with zipfile.ZipFile(ipsw, 'r') as zf:
            try:
                zf.getinfo('BuildManifest.plist')
            except (KeyError, zipfile.BadZipFile):
                raise NotAnIPSW(ipsw)

            yield zf

    except zipfile.BadZipFile:
        raise NotAnIPSW(ipsw)
