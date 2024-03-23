import xconf
import pathlib
from ._base import BaseCommand
from datetime import timezone
import datetime
import logging
import os
import psycopg2
import socket
from ..core import FileOrigin

log = logging.getLogger(__name__)

@xconf.config
class Verify(BaseCommand):
    '''Compare a replica to the database
    '''

    def find_new_files(self, paths):
        new_files = []
        for fp in paths:
            with self.con.cursor() as c:
                c.execute("SELECT COUNT(*) FROM file_inventory WHERE origin_host = %s AND origin_path = %s", (self.hostname, fp))
                count = c.fetchone()
                if count == 0:
                    new_files.append(FileOrigin(origin_host=self.hostname, origin_path=fp, mtime_sec=os.stat(fp).st_mtime))
        return new_files

    def update_inventory(self, new_files: list[dict]):
        with self.con.cursor() as c:
            c.executemany(
                "INSERT INTO file_inventory (origin_host, origin_path, mtime_sec) VALUES (%s, %s, %s)",
                [(f.origin_host, f.origin_path, f.mtime_sec) for f in new_files]
            )

    def verify(self):
        pass

    def main(self):
        self.con = self.db.connect()
        self.hostname = socket.gethostname()

        self.scan()