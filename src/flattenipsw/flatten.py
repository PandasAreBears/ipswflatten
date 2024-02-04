from contextlib import contextmanager
from pathlib import Path
from typing import Generator, Iterator
import zipfile
from flattenipsw.exception import NotAnIPSW
import shutil
import logging

logger = logging.getLogger(__name__)

@contextmanager
def ipsw_unzip_context(ipsw: Path, out: Path | None = None) -> Generator[Path, None, None]:
    yield (output := ipsw_unzip(ipsw=ipsw, out=out))

    logging.info(f"Cleaning up extracted IPSW at {output}")
    shutil.rmtree(output)

def ipsw_unzip(ipsw: Path, out: Path | None = None) -> Path:
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

        logger.info(f"Extracting IPSW to {out}")
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
