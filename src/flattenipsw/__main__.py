import sys
from pathlib import Path
sys.path.append(str(Path(__file__).parent.parent))

import click
import click_pathlib
from flattenipsw.flatten import ipsw_unzip_context
from flattenipsw.extract import ipsw_build_dmg_path, ipsw_mount_dmg_context, ipsw_split_shared_cache
from flattenipsw.crawl import ipsw_copy_shared_cache, ipsw_crawl_filesystem, BinaryFileRule
import logging

logging.basicConfig(level=logging.INFO)

@click.command
@click.option("--ipsw", type=click_pathlib.Path(), required=True)
@click.option("--output", type=click_pathlib.Path(), default=None)
def main(ipsw: Path, output: Path | None = None):

    if output is None:
        output = ipsw.parent / "output"
        output.mkdir(exist_ok=True)

    binaries_folder = output / "binaries"
    dyld_folder = output / "dyld_shared_cache"
    dyld_split = output / "split_dyld_cache"

    with ipsw_unzip_context(ipsw=ipsw) as unzipped:
        dmg_path = ipsw_build_dmg_path(unzipped)

        with ipsw_mount_dmg_context(dmg_path.filesystem) as mount_point:
            ipsw_crawl_filesystem(mount_point, rule=BinaryFileRule(), output=binaries_folder)

            if dmg_path.dyld_shared_cache is None:
                ipsw_copy_shared_cache(mount_point, dyld_folder)

        if dmg_path.dyld_shared_cache is not None:
            with ipsw_mount_dmg_context(dmg_path.dyld_shared_cache) as mount_point:
                ipsw_copy_shared_cache(mount_point, dyld_folder)

        ipsw_split_shared_cache(dyld_folder, dyld_split)





if __name__ == "__main__":
    main()