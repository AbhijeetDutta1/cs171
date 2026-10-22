"""Per-node log in wall-clock processing order, in the format of the assignment's sample poet.log."""

import os

from config import LOG_DIR


def fmt(clock):
    return "[" + ",".join(map(str, clock)) + "]"


class Log:
    def __init__(self, name):
        os.makedirs(LOG_DIR, exist_ok=True)
        self.name = name
        self.f = open(os.path.join(LOG_DIR, f"{name.lower()}.log"), "w")
        self.n = 0

    def _write(self, kind, rest):
        self.n += 1
        line = f"#{self.n:<3} {kind:<7} {rest}"
        self.f.write(line + "\n")
        self.f.flush()
        print(f"[{self.name}] {line}", flush=True)

    def send(self, to, clock, text, remaining):
        """clock = this node's clock AFTER the update for the send."""
        self._write("SEND", f"-> {to:<6} clock={fmt(clock):<10} '{text}'  remaining={remaining}")

    def recv(self, frm, msg_clock, text, remaining, local_clock):
        """msg_clock = clock attached to the message; local_clock = this node's clock on arrival."""
        self._write("RECV", f"<- {frm:<6} clock={fmt(msg_clock):<10} '{text}'  remaining={remaining}"
                            f"  {self.name.lower()}_clock={fmt(local_clock)}")

    def output(self, frm, msg_clock, text, local_clock, held):
        """Poet only: a verse is appended to the poem. held=True if it waited in the hold-back queue."""
        self._write("OUTPUT", f"   {frm:<6} clock={fmt(msg_clock):<10} '{text}'"
                              f"  {self.name.lower()}_clock={fmt(local_clock)}  held={held}")
