import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import click
import click_pathlib
from flattenipsw.flatten import ipsw_unzip_context
from flattenipsw.extract import ipsw_build_dmg_path, ipsw_mount_dmg_context
from flattenipsw.crawl import ipsw_crawl_filesystem, BINARY_FILE_HANDLERS
import logging

logging.basicConfig(level=logging.INFO)

@click.command
@click.option("--ipsw", type=click_pathlib.Path(), required=True)
@click.option("--output", type=click_pathlib.Path(), default=None)
def main(ipsw: Path, output: Path | None = None):

    with ipsw_unzip_context(ipsw=ipsw) as unzipped:
        dmg_path = ipsw_build_dmg_path(unzipped)
        logging.info(dmg_path.dyld_shared_cache)

        with ipsw_mount_dmg_context(dmg_path.filesystem) as mount_point:
            ipsw_crawl_filesystem(mount_point, file_handlers=BINARY_FILE_HANDLERS, output=output)

        if dmg_path.dyld_shared_cache is not None:
            with ipsw_mount_dmg_context(dmg_path.dyld_shared_cache) as mount_point:
                ipsw_crawl_filesystem(mount_point, file_handlers=BINARY_FILE_HANDLERS, output=output)



if __name__ == "__main__":
    main()