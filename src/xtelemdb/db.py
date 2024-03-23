import os
import typing
import atexit
import xconf
import logging
import psycopg2

log = logging.getLogger(__name__)

_exit_handler_installed = set()

@xconf.config
class DbConfig:
    host : str = xconf.field(default='localhost', help='Hostname on which PostgreSQL is listening for connections')
    user : str = xconf.field(default='xsup', help='Username with access to PostgreSQL database over TCP')
    port : int = xconf.field(default=5432, help='TCP port to connect to PostgreSQL on')
    database : int = xconf.field(default='xtelem', help='Name of PostgreSQL database')

    def connect(self):
        password = os.environ.get('XTELEMDB_PASSWORD', None)
        if password is None:
            raise RuntimeError(f"Need password to connect to host={self.host} database={self.database} user={self.user}, set $XTELEMDB_PASSWORD in the environment")
        return psycopg2.connect(
            database=self.database,
            host=self.host,
            user=self.user,
            password=password,
        )
