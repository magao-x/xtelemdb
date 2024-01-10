import sqlite3
import typing
import atexit
import xconf
import logging

log = logging.getLogger(__name__)

_exit_handler_installed = set()

@xconf.config
class SqliteConfig(xconf.FileConfig):
    def connect(self) -> sqlite3.Connection:
        conn = sqlite3.connect(self.path)
        conn.row_factory = sqlite3.Row

        # ensure the optimize hook runs once per connected path
        if self.path not in _exit_handler_installed:
            def _exit_handler():
                conn.cursor().execute("PRAGMA OPTIMIZE;")
                conn.close()
            atexit.register(_exit_handler)
            _exit_handler_installed.add(self.path)
        return conn

    def cursor(self) -> sqlite3.Cursor:
        return self.connect().cursor()
