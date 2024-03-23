import xconf
import pathlib
from ._base import BaseCommand
from datetime import timezone
import datetime
import logging
import psycopg2
log = logging.getLogger(__name__)

@xconf.config
class Ingest(BaseCommand):
    '''Ensure the file replicas found on this host have been ingested since they
    were inventoried
    '''

    def main(self):
        self.con = self.db.connect()
        