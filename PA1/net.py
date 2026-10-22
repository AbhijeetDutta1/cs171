"""Socket plumbing. Each node listens on its own TCP port; incoming messages land in a queue.

Communication properties worth knowing for the demo:
  * Every message opens a NEW TCP connection and is sent after its own random delay, from its
    own thread. So there is NO FIFO guarantee: two messages from A to B can arrive in either
    order. Reliability: messages are not lost (TCP, with connect retries).
  * Messages are JSON dicts. They are serialized at the moment you call send(), so changing your
    clock afterwards does not change a message that is still "in flight".
"""

import json
import queue
import random
import socket
import threading
import time

from config import HOST, PORTS, MIN_DELAY, MAX_DELAY


class Node:
    def __init__(self, name):
        self.name = name
        self.inbox = queue.Queue()
        self._server = socket.socket(socket.AF_INET, socket.SOCK_STREAM)
        self._server.setsockopt(socket.SOL_SOCKET, socket.SO_REUSEADDR, 1)
        self._server.bind((HOST, PORTS[name]))
        self._server.listen()
        threading.Thread(target=self._accept_loop, daemon=True).start()

    def _accept_loop(self):
        while True:
            conn, _ = self._server.accept()
            threading.Thread(target=self._read, args=(conn,), daemon=True).start()

    def _read(self, conn):
        # The sender closes the connection after one message, so read until EOF.
        chunks = []
        with conn:
            while data := conn.recv(4096):
                chunks.append(data)
        self.inbox.put(json.loads(b"".join(chunks)))

    def recv(self, timeout=None):
        """Block until a message arrives (in arrival order). Raises queue.Empty on timeout."""
        return self.inbox.get(timeout=timeout)

    def send(self, dest, msg, delay=None):
        """Send msg to dest after a random delay. Returns immediately (non-blocking)."""
        payload = json.dumps(msg).encode()
        if delay is None:
            delay = random.uniform(MIN_DELAY, MAX_DELAY)
        threading.Thread(target=_deliver, args=(dest, payload, delay), daemon=True).start()


def _deliver(dest, payload, delay):
    time.sleep(delay)
    for _ in range(50):  # the destination may not be listening yet at startup
        try:
            with socket.create_connection((HOST, PORTS[dest])) as s:
                s.sendall(payload)
            return
        except ConnectionRefusedError:
            time.sleep(0.1)
    raise RuntimeError(f"could not reach {dest}")
