"""An agent (Happy, Sad, or Love). Usage: python3 agent.py Happy

The agent handles one message at a time from its inbox, so there are no races on self.clock.
"""

import random
import sys
import time

from config import AGENTS, INDEX, MIN_PROCESS, MAX_PROCESS
from logger import Log
from net import Node
from words import next_verse


class Agent:
    def __init__(self, name):
        self.name = name
        self.me = INDEX[name]          # my position in the vector clock
        self.node = Node(name)
        self.log = Log(name)

        # [TODO 1 - done] Vector clock initialization.
        #   Implemented: a 3-entry clock [Happy, Sad, Love], all zeros.
        #   Why: only agents create events (verses), so only agents need an entry. The Poet
        #   writes no verses, which is why its requests in the sample carry [0,0,0].
        self.clock = [0] * len(AGENTS)

    def run(self):
        while True:
            msg = self.node.recv()
            self.log.recv(msg["from"], msg["clock"], msg["text"], msg["remaining"], self.clock)
            self.on_receive(msg)
            self.write_verse(msg)

    def on_receive(self, msg):
        # [TODO 2 - done] Receive rule.
        #   Implemented: merge = element-wise max of my clock and the message's clock.
        #   Why: after this, my clock reflects everything that causally happened before the
        #   message, so my next verse is ordered after the verse I just received.
        #   A REQUEST carries [0,0,0], so merging it changes nothing (no special case needed).
        self.clock = [max(mine, theirs) for mine, theirs in zip(self.clock, msg["clock"])]

    def write_verse(self, msg):
        prev = msg["prefix"] if msg["type"] == "REQUEST" else msg["text"]
        time.sleep(random.uniform(MIN_PROCESS, MAX_PROCESS))
        verse = next_verse(prev, self.name)
        remaining = msg["remaining"] - 1

        # [TODO 3 - done] Event rule.
        #   Implemented: increment my own entry by 1.
        #   Why: writing a verse is a local event. It happens exactly once, even though two
        #   messages go out, because the spec treats both sends as one operation.
        self.clock[self.me] += 1

        # [TODO 4 - done] Message timestamp.
        #   Implemented: attach a COPY of my clock (after the increment) to the outgoing message.
        #   Why: both messages carry the same vector time. A copy means the value in the
        #   message and the log can't change if self.clock is modified later.
        stamp = list(self.clock)

        out = {"type": "VERSE", "from": self.name, "text": verse,
               "remaining": remaining, "clock": stamp}

        # Two sends with independent random delays: either one can arrive first.
        self.node.send("Poet", out)
        self.log.send("Poet", stamp, verse, remaining)
        if remaining > 0:
            nxt = random.choice([a for a in AGENTS if a != self.name])
            self.node.send(nxt, out)
            self.log.send(nxt, stamp, verse, remaining)


if __name__ == "__main__":
    Agent(sys.argv[1]).run()
