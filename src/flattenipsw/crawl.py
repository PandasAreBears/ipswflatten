
from abc import ABC, abstractmethod
from pathlib import Path
import shutil
import subprocess
from typing import Sequence
import json
import logging

logger = logging.getLogger(__name__)


class FileHandler(ABC):
    """An abstract class for handling files encountered during an IPSW crawl. 
    
    The handler is called when a file is encountered that matches the `file_type` or `file_name` signatures.

    If multiple handlers match a file, then all matching handler will be called. The order of the handlers is not guaranteed.
    """
    @property
    def file_type(self) -> str | None:
        """If the result of calling `file` contains this string, then this handler will be used.
        
        Returns:
            str | None: The file type signature. None if not used.
        """
        return None
        

    @property
    def file_name(self) -> str | None:
        """If the file name contains this string, then this handler will be used.
        
        Returns:
            str | None: The file name signature. None if not used.
        """
        return None

    @abstractmethod
    def handle_file(self, file: Path, output: Path) -> list[str]:
        """The handler called when a matching file is found.

        Args:
            file (Path): The file to handle.
            output (Path): The output directory to emit files to.

        Returns:
            list[str]: A list of file names that were emitted.
        """
        pass


class BinaryFileHandler(FileHandler):
    @property
    def file_type(self) -> str:
        return "Mach-O"

    def handle_file(self, file: Path, output: Path) -> list[str]:
        """Copy binary files to the output directory."""
        shutil.copy(file, output / file.name)

        return [file.name]

class DyldSharedCacheHandler(FileHandler):
    @property
    def file_name(self) -> str:
        return "dyld_shared_cache_arm64"
    
    def handle_file(self, file: Path, output: Path) -> list[str]:
        # ignore file that don't exactly match
        if file.name != self.file_name:
            logger.info(f"Skipping {file} because it does not exactly match {self.file_name}")
            return []

        command = f"dyldex_all {file}"
        subprocess.run(command, shell=True, check=True)

        # Run dyldex_all creates a folder named 'binaries' in the current directory.
        files = []
        for file in (file.parent / "binaries").rglob("*"):
            if "Mach-O" in _ipsw_get_file_type(file):
                shutil.copy(file, output / file.name)
                files.append(file.name)

        return files

BINARY_FILE_HANDLERS = [
    BinaryFileHandler(),
    DyldSharedCacheHandler()
]
    

def ipsw_crawl_filesystem(mount_point: Path, file_handlers: Sequence[FileHandler], output: Path | None = None) -> Path:
    """Crawl the filesystem and copy all 

    Args:
        mount_point (Path): The path to the mounted filesystem.
        output (Path): The output directory to emit files to.

    Returns:
        Path: The output directory.
    """
    if output is None:
        output = mount_point.parent / "bin"

    output.mkdir(exist_ok=True)

    # Tracks the original location of an emitted file.
    locations: dict[str, str] = {}

    for file in mount_point.rglob("*"):
        for handler in file_handlers:
            if handler.file_type is not None:
                if handler.file_type in _ipsw_get_file_type(file):
                    logger.info(f"Invoking handler {handler.__class__.__name__} for matched file type on {file}")
                    try:
                        emissions = handler.handle_file(file, output)
                        locations |= {str(file.relative_to(mount_point)): emission for emission in emissions}
                        logger.info(f"Emitted {len(emissions)} file{'s' if len(emissions) else ''} from {file} to {output}")
                    except Exception as e:
                        logger.error(f"Error handling file {file}: {e}")

            if handler.file_name is not None:
                if handler.file_name in file.name:
                    logger.info(f"Invoking handler {handler.__class__.__name__} for matched file name on {file}")
                    try:
                        emissions = handler.handle_file(file, output)
                        locations |= {str(file.relative_to(mount_point)): emission for emission in emissions}
                        logger.info(f"Emitted {len(emissions)} file{'s' if len(emissions) else ''} from {file} to {output}")
                    except Exception as e:
                        logger.error(f"Error handling file {file}: {e}")


    locations_file = output / "locations.json"
    current = {}
    if locations_file.exists():
        with open(locations_file, "r") as f:
            current = json.load(f)
    
    with open(locations_file, "w") as f:
        f.write(json.dumps(current | locations, indent=4))

    return output


def _ipsw_get_file_type(path: Path) -> str:
    """Calls the `file` command on the file and returns the result.

    Args:
        path (Path): The path to the file.

    Returns:
        str: The result of the `file` command.
    """
    return subprocess.run(["file", path], capture_output=True, text=True).stdout