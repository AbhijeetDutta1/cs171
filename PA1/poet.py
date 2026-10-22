"""The Poet. Sends requests, then outputs verses in a causally consistent order.

Usage:
  python3 poet.py 1 [--n 5]          one request (FIRST) to a random agent
  python3 poet.py 2 [--n 3 4 5]      FIRST->Happy, SECOND->Sad, THIRD->Love, concurrently
"""

import argparse
import os
import queue
import random

from config import AGENTS, LOG_DIR
from logger import Log, fmt
from net import Node

PREFIXES = ["FIRST", "SECOND", "THIRD"]


class Poet:
    def __init__(self, requests):
        self.requests = requests       # list of (agent, prefix, n)
        self.node = Node("Poet")
        self.log = Log("Poet")

        # TODO(you): initialize the Poet's vector clock.
        self.clock = [0] * len(AGENTS)

        self.held = []                 # hold-back queue: received but not yet deliverable
        self.poem = []                 # (verse, clock) in output order

    def run(self):
        for agent, prefix, n in self.requests:
            text = f"REQUEST {prefix} n={n}"
            msg = {"type": "REQUEST", "from": "Poet", "prefix": prefix, "text": text,
                   "remaining": n, "clock": list(self.clock)}
            self.node.send(agent, msg)
            self.log.send(agent, self.clock, text, n)

        total = sum(n for _, _, n in self.requests)
        while len(self.poem) < total:
            try:
                msg = self.node.recv(timeout=20)
            except queue.Empty:
                print(f"\n[Poet] STUCK: no message for 20s. poet_clock={fmt(self.clock)}")
                for m in self.held:
                    print(f"  still held: {m['from']} clock={fmt(m['clock'])} '{m['text']}'")
                break
            self.log.recv(msg["from"], msg["clock"], msg["text"], msg["remaining"], self.clock)
            self.held.append(msg)
            self.deliver_ready(just_arrived=msg)

        with open(os.path.join(LOG_DIR, "poem.txt"), "w") as f:
            for verse, clock in self.poem:
                f.write(f"{verse:<45} {fmt(clock)}\n")

    def can_deliver(self, msg):
        # TODO(you): the causal delivery condition.
        #   Given self.clock and msg["clock"] (sent by agent msg["from"]), may this verse be
        #   output now, or is it missing something that causally precedes it?
        return True

    def deliver(self, msg, held):
        # TODO(you): update self.clock now that this verse is part of the poem.

        self.poem.append((msg["text"], msg["clock"]))
        self.log.output(msg["from"], msg["clock"], msg["text"], self.clock, held)

    def deliver_ready(self, just_arrived):
        # TODO(you): this makes ONE pass over the hold-back queue. Is that enough?
        #   Hint: can delivering one verse make a different held verse deliverable?
        for msg in list(self.held):
            if self.can_deliver(msg):
                self.held.remove(msg)
                self.deliver(msg, held=msg is not just_arrived)


def build_requests(mode, ns):
    if mode == 1:
        return [(random.choice(AGENTS), "FIRST", ns[0] if ns else 5)]
    ns = ns or [3, 4, 5]
    return [(AGENTS[i], PREFIXES[i], ns[i]) for i in range(3)]


if __name__ == "__main__":
    p = argparse.ArgumentParser()
    p.add_argument("mode", type=int, choices=[1, 2])
    p.add_argument("--n", type=int, nargs="*")
    args = p.parse_args()
    Poet(build_requests(args.mode, args.n)).run()
