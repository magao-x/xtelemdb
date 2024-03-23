import xconf
import pathlib
from ._base import BaseCommand, DEFAULT_DATA_DIRS
from datetime import timezone
import datetime
import logging
import os
import os.path
import psycopg2
import socket
from tqdm import tqdm
from ..core import FileOrigin

log = logging.getLogger(__name__)

@xconf.config
class Inventory(BaseCommand):
    '''Find files that aren't yet ingested and inventory them
    '''
    data_dirs : list[str] = xconf.field(default_factory=lambda: DEFAULT_DATA_DIRS)

    def find_new_files(self, paths):
        new_files = []
        base_dir = os.path.dirname(paths[0]) if len(paths) else ''
        for fp in tqdm(paths, desc=base_dir):
            with self.con.cursor() as c:
                c.execute("SELECT COUNT(*) FROM file_inventory WHERE origin_host = %s AND origin_path = %s", (self.hostname, fp))
                count = c.fetchone()[0]
                if count == 0:
                    new_files.append(FileOrigin(origin_host=self.hostname, origin_path=fp, mtime_sec=os.stat(fp).st_mtime))
        return new_files

    def update_inventory(self, new_files: list[dict]):
        with self.con.cursor() as c:
            c.executemany(
                "INSERT INTO file_inventory (origin_host, origin_path, modification_time) VALUES (%s, %s, TO_TIMESTAMP(%s))",
                [(f.origin_host, f.origin_path, f.mtime_sec) for f in new_files]
            )
            c.execute("COMMIT")

    def scan(self):
        for prefix in self.data_dirs:
            for dirpath, dirnames, filenames in os.walk(prefix):
                new_files = self.find_new_files([os.path.join(dirpath, fn) for fn in filenames])
                log.info(f"Found {len(new_files)} new files in {dirpath}")
                self.update_inventory(new_files)

    def main(self):
        self.con = self.database.connect()
        self.scan()