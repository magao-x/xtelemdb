import time
import xconf
import socket
import threading
from queue import Queue
from ._base import BaseCommand
from datetime import timezone
import logging
log = logging.getLogger(__name__)

RETRY_CONNECTION_WAIT_SEC = 2

def _connection(sock, q):
    buf = b''
    while True:
        buf += sock.recv(4096)
        parts = buf.split(b'\n')
        if len(parts) < 2:
            continue
        for part in parts[:-1]:
            try:
                q.put(part.decode('utf8'))
            except Exception as e:
                log.exception(f"Could not decode bytes: {repr(part)}")
        buf = parts[-1]

def _serve(host, port, q):
    while True:
        try:
            log.info(f"Listening for connections on {host}:{port}")
            sock = socket.create_server((host, port), reuse_port=True)
            while True:
                new_sock, addrinfo = sock.accept()
                log.info(f"New connection from {addrinfo}")
                t = threading.Thread(target=_connection, args=(new_sock, q), daemon=True)
                t.start()
        except Exception as e:
            log.exception(f"Could not accept connections on {host}:{port}, retrying in {RETRY_CONNECTION_WAIT_SEC} sec")
            time.sleep(RETRY_CONNECTION_WAIT_SEC)

@xconf.config
class Listen(BaseCommand):
    '''Accept log and telemetry messages over a TCP socket
    '''
    host : str = xconf.field(default="localhost", help="Hostname or IP to bind to")
    port : int = xconf.field(default=60100, help="Hostname or IP to bind to")

    def main(self):
        q = Queue()
        serve_thread = threading.Thread(target=_serve, args=(self.host, self.port, q,))
        serve_thread.start()
        while True:
            msg : str = q.get()
            print(msg)
