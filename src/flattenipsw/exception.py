
from pathlib import Path

class IPSWFlattenException(Exception):
    pass

class NotAnIPSW(IPSWFlattenException):
    def __init__(self, path: Path):
        self.path = path
        super().__init__(f'{path} is not an IPSW file.')

class InvalidBuildManfest(IPSWFlattenException):
    def __init__(self, path: Path, key: str):
        self.path = path
        super().__init__(f'{path} is not a valid BuildManifest.plist file. It is missing the key {key}.')

