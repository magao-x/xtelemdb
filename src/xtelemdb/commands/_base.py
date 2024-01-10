import xconf
from .. import db

@xconf.config
class BaseCommand(xconf.Command):
    '''Base class for telemdb commands providing a `db` config item
    '''
    # database : db.SqliteConfig = xconf.field(default=db.DEFAULT_DB_CONFIG)

    def main(self):
        raise NotImplementedError("Command subclasses must implement main()")
