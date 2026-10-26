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

        # [TODO 5 - done] Poet's vector clock initialization.
        #   Implemented: a 3-entry clock [Happy, Sad, Love], all zeros.
        #   Meaning: clock[j] = how many of agent j's verses have been OUTPUT to the poem so far
        #   (outputs, not receives: verses in the hold-back queue don't count yet).
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
        # [TODO 6 - done] Causal delivery condition (same idea as causal broadcast, BSS).
        #   Implemented: a verse from agent j with clock m can be output only if
        #     (a) m[j] == clock[j] + 1   -> it is the NEXT verse from j (no earlier j verse missing)
        #     (b) m[k] <= clock[k], k!=j -> every verse from other agents that it depends on
        #                                   has already been output
        #   Otherwise it stays in the hold-back queue.
        j = AGENTS.index(msg["from"])
        m = msg["clock"]
        if m[j] != self.clock[j] + 1:
            return False
        return all(m[k] <= self.clock[k] for k in range(len(AGENTS)) if k != j)

    def deliver(self, msg, held):
        # [TODO 7 - done] Update the Poet's clock on output.
        #   Implemented: clock[j] = m[j] for the sender j (i.e., one more verse from j output).
        #   Why it's enough: can_deliver already guarantees m[k] <= clock[k] for every other k,
        #   so an element-wise max would only change entry j. It gives the same result.
        j = AGENTS.index(msg["from"])
        self.clock[j] = msg["clock"][j]

        self.poem.append((msg["text"], msg["clock"]))
        self.log.output(msg["from"], msg["clock"], msg["text"], self.clock, held)

    def deliver_ready(self, just_arrived):
        # [TODO 8 - done] Hold-back queue release loop.
        #   Implemented: repeatedly sweep the held verses, outputting any that are deliverable,
        #   until a full pass outputs nothing.
        #   Why: outputting one verse advances the Poet's clock, which can unblock another held
        #   verse, which can unblock a third (a chain reaction). A single pass could miss them.
        #   held=True in the log means the verse waited; held=False means it went out on arrival.
        delivered = True
        while delivered:
            delivered = False
            for msg in list(self.held):
                if self.can_deliver(msg):
                    self.held.remove(msg)
                    self.deliver(msg, held=msg is not just_arrived)
                    delivered = True


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
