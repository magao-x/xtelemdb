import socket

import psycopg2
import xconf

from .. import db

DEFAULT_DATA_DIRS = [
    '/opt/MagAOX/logs',
    '/opt/MagAOX/rawimages',
    '/opt/MagAOX/telem',
    '/opt/MagAOX/cacao',
]

@xconf.config
class BaseCommand(xconf.Command):
    '''Base class for telemdb commands providing a `db` config item
    '''
    database : db.DbConfig = xconf.field(default=db.DbConfig(), help="PostgreSQL database connection")
    hostname : str = xconf.field(default=socket.gethostname(), help="Hostname to use for this computer when running inventory or watch_files")

    def main(self):
        raise NotImplementedError("Command subclasses must implement main()")
