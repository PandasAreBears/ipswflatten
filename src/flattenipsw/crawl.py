
import re
from abc import ABC
from pathlib import Path
import shutil
import subprocess
from typing import Sequence
from flattenipsw.exception import FailedToCreateOutputDirectory
import logging

logger = logging.getLogger(__name__)


class FileRule(ABC):
    """An abstract class for defining which files to copy during an ipsw crawl."""
    @property
    def file_type(self) -> str | None:
        """If the result of calling `file` matches this regular expression, then the file will be copied.
        
        Returns:
            str | None: The file type regex. None if not used.
        """
        return None
        

    @property
    def file_name(self) -> str | None:
        """If the file name matches this regular expression, then the file will be copied.
        
        Returns:
            str | None: The file name regex. None if not used.
        """
        return None

    @property
    def invert_file_name(self) -> bool:
        """If True, the file will be copied if the file name does not match the regular expression in `file_name`.
        
        Returns:
            bool: Whether to invert the file name match.
        """
        return False

    @property
    def invert_file_type(self) -> bool:
        """If True, the file will be copied if the file type does not match the regular expression in `file_type`.
        
        Returns:
            bool: Whether to invert the file type match.
        """
        return False

    def evaluate(self, file: Path) -> bool:
        """Evaluate whether the file should be copied.

        Args:
            file (Path): The file to evaluate.

        Returns:
            bool: Whether the file should be copied.
        """
        return self._evaluate_file_name(file) and self._evaluate_file_type(file)

    def _evaluate_file_name(self, file: Path) -> bool:
        """Evaluate the file name match.

        Args:
            file (Path): The file to evaluate.

        Returns:
            bool: Whether the file name matches the rule. Defaults to True if `file_name` is None.
        """
        if self.file_name is not None:
            return (re.match(self.file_name, file.name) is not None) == (not self.invert_file_name)
        return True

    def _evaluate_file_type(self, file: Path) -> bool:
        """Evaluate the file type match.

        Args:
            file (Path): The file to evaluate.

        Returns:
            bool: Whether the file type matches the rule. Defaults to True if `file_type` is None.
        """
        if self.file_type is not None:
            return (re.match(self.file_type, _ipsw_get_file_type(file)) is not None) == (not self.invert_file_type)
        return True

class BinaryFileRule(FileRule):
    @property
    def file_type(self) -> str:
        return "Mach-O"

    @property
    def file_name(self) -> str:
        return "dyld_shared_cache_arm64.*"

    @property
    def invert_file_name(self) -> bool:
        return True

class DyldSharedCacheRule(FileRule):
    @property
    def file_name(self) -> str:
        return "dyld_shared_cache_arm64.*"
    

def ipsw_crawl_filesystem(mount_point: Path, rule: FileRule, output: Path) -> dict[Path, Path]:
    """Crawl the filesystem and copy all files matching the provided rules to the output directory.

    Args:
        mount_point (Path): The path to the mounted filesystem.
        rule (FileRule): The rule to use to determine which files to copy.
        output (Path): The output directory to emit files to.

    Returns:
         dict[Path, Path]: A dictionary of the original file location to the emitted file location.
    """
    output.mkdir(exist_ok=True)
    
    if not output.is_dir():
        raise FailedToCreateOutputDirectory(output)

    # Tracks the original location of an emitted file.
    locations: dict[Path, Path] = {}

    for file in mount_point.rglob("*"):
        if rule.evaluate(file):
            logger.info(f"Rule {rule.__class__.__name__} matched file type on {file}")
            shutil.copy(file, output / file.name)
            locations[file.relative_to(mount_point)] = output / file.name

    return locations


def _ipsw_get_file_type(path: Path) -> str:
    """Calls the `file` command on the file and returns the result.

    Args:
        path (Path): The path to the file.

    Returns:
        str: The result of the `file` command.
    """
    return subprocess.run(["file", "-b", path], capture_output=True, text=True).stdout