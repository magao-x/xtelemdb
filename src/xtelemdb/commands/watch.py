import json
import xconf
import subprocess
import queue
import socket
import threading
import pathlib
import time
import os.path
import os
import sys
from ._base import BaseCommand
from datetime import timezone
import datetime
from watchdog.observers import Observer
from watchdog.events import FileSystemEventHandler
import logging
import psycopg2
from .sqlMain import data_input
log = logging.getLogger(__name__)

class NewXFilesHandler(FileSystemEventHandler):
    def __init__(self, events_queue):
        self.events_queue = events_queue

    def construct_message(self, event, is_new_file=False):
        stat_result = os.stat(event.src_path)
        msg = {
            "device": "filesystem",
            "ts": datetime.datetime.now().isoformat() + "000",  # zeros for consistency with MagAO-X timestamps with ns
            "ec": "file_created" if is_new_file else "file_modified",
            "msg": {
                "file": os.path.basename(event.src_path),
                "size_bytes": stat_result.st_size,
                "mtime": datetime.datetime.fromtimestamp(stat_result.st_mtime).isoformat() + "000",
            }
        }
        msg_json = json.dumps(msg)
        log.debug(msg_json)
        return (msg_json + '\n').encode('utf8')

    def on_created(self, event):
        if event.is_directory:
            return
        self.events_queue.put(self.construct_message(event, is_new_file=True))

    def on_modified(self, event):
        if event.is_directory:
            return
        self.events_queue.put(self.construct_message(event, is_new_file=False))

RETRY_CONNECTION_WAIT_SEC = 2
CREATE_CONNECTION_TIMEOUT_SEC = 2

def _run_logdump_thread(logdump_args, name, message_queue):
    log.debug(f"Running logdump for {name} in follow mode")
    p = subprocess.Popen(logdump_args + ['-J', '-f', name], stdout=subprocess.PIPE, stdin=subprocess.DEVNULL, stderr=subprocess.DEVNULL)
    name_bytes = name.encode('utf8')
    for line in p.stdout:
        assert line[0] == ord('{'), f'malformed line {line[0]=}'
        outbound_line = b'{"device": "' + name_bytes + b'", ' + line[1:]
        log.debug(f"{outbound_line=}")
        message_queue.put(outbound_line)
 
def _run_connection_thread(host, port, q):   ###add outside commands to feed to db instead of listen
    print(f"{host=} {port=}")
    while True:
        log.info(f"Connected to {host}:{port}")
        try:
            with psycopg2.connect(**db_params) as conn:
                with conn.cursor() as cur:
                    while line := q.get():
                        #data = extract_msg(line)
                        print(line)
                        data_input(line, cur, conn)
                        #print("data", line)
                    cur.commit()
        except Exception as e:
            log.exception(f"Creating connection to {host}:{port} failed, retrying in {RETRY_CONNECTION_WAIT_SEC}")
            time.sleep(RETRY_CONNECTION_WAIT_SEC)

@xconf.config
class Watch(BaseCommand):
    '''Keep an eye on the X files and insert to a database
    '''
    proclist : str = xconf.field(default="/opt/MagAOX/config/proclist_%s.txt", help="Path to process list file, %s will be replaced with the value of $MAGAOX_ROLE (or an empty string if absent from the environment)")
    logdump_exe : str = xconf.field(default="/opt/MagAOX/bin/logdump", help="logdump (a.k.a. teldump) executable to use")

    def main(self):
        self.con = self.db.connect()

        role = os.environ.get('MAGAOX_ROLE', '')
        proclist = pathlib.Path(self.proclist.replace('%s', role))
        if not proclist.exists():
            raise RuntimeError(f"No process list at {proclist}")

        device_names = set()

        with proclist.open() as fh:
            for line in fh:
                if not line.strip():
                    continue
                if line.strip()[0] == '#':
                    continue
                parts = line.split(None, 1)
                if len(parts) != 2:
                    raise RuntimeError(f"Got malformed proclist line: {repr(line)}")
                device_names.add(parts[0])
        q = queue.Queue()
        all_threads = []
        for dev in device_names:
            log_thread = threading.Thread(target=_run_logdump_thread, args=([self.logdump_exe], dev, q))
            # log_thread.start()
            all_threads.append(log_thread)
            telem_thread = threading.Thread(target=_run_logdump_thread, args=([self.logdump_exe, '--dir=/opt/MagAOX/telem', '--ext=.bintel'], dev, q))
            # telem_thread.start()
            all_threads.append(telem_thread)

        conn_thread = threading.Thread(target=_run_connection_thread, args=(self.host, self.port, q))
        # conn_thread.start()
        all_threads.append(conn_thread)

        event_handler = NewXFilesHandler(q)
        observer = Observer()
        for dirpath in self.watch_dirs:
            observer.schedule(event_handler, dirpath, recursive=True)
            log.info(f"Watching {dirpath} for changes")
        all_threads.append(observer)

        try:
            for t in all_threads:
                t.start()
        finally:
            for t in all_threads:
                t.join()
