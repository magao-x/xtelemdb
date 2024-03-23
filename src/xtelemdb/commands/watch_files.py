import xconf
import os.path
import os
from ._base import BaseCommand, DEFAULT_DATA_DIRS
from datetime import timezone
import datetime
from watchdog.observers.polling import PollingObserver
from watchdog.events import FileSystemEventHandler
import logging
import psycopg2
from .sqlMain import data_input
log = logging.getLogger(__name__)

class NewXFilesHandler(FileSystemEventHandler):
    def __init__(self, conn, hostname):
        self.conn = conn
        self.hostname = hostname

    def insert_file(self, file_path, size_bytes, mtime_sec):
        log.info(f"Got {file_path} new")
        with self.conn.cursor() as cur:
            cur.execute(
                "INSERT INTO file_inventory (origin_host, origin_path, size_bytes, modification_time) VALUES (%s, %s, %s, TO_TIMESTAMP(%s))",
                (self.hostname, file_path, size_bytes, mtime_sec)
            )
            cur.execute("COMMIT")

    def update_file(self, file_path, size_bytes, mtime_sec):
        log.info(f"Got {file_path} update")
        with self.conn.cursor() as cur:
            cur.execute(
                "UPDATE file_inventory SET size_bytes = %s, modification_time = TO_TIMESTAMP(%s) WHERE origin_host = %s AND origin_path = %s",
                (size_bytes, mtime_sec, self.hostname, file_path)
            )
            cur.execute("COMMIT")

    def _get_meta(self, file_path):
        stat_result = os.stat(file_path)
        size_bytes = stat_result.st_size
        mtime_sec = stat_result.st_mtime
        return file_path, size_bytes, mtime_sec

    def on_created(self, event):
        if event.is_directory:
            return
        self.insert_file(*self._get_meta(event.src_path))

    def on_modified(self, event):
        if event.is_directory:
            return
        self.update_file(*self._get_meta(event.src_path))

@xconf.config
class WatchFiles(BaseCommand):
    '''Monitor filesystem for new and changed files
    '''
    data_dirs : list[str] = xconf.field(default_factory=lambda: DEFAULT_DATA_DIRS)

    def main(self):
        self.conn = self.database.connect()

        event_handler = NewXFilesHandler(self.conn, self.hostname)
        observer = PollingObserver()
        for dirpath in self.data_dirs:
            observer.schedule(event_handler, dirpath, recursive=True)
            log.info(f"Watching {dirpath} for changes")
        try:
            observer.start()
        finally:
            observer.join()
