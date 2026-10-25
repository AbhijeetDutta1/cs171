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

        # One entry per agent [Happy, Sad, Love]. The Poet writes no verses, so it gets no entry.
        self.clock = [0] * len(AGENTS)

    def run(self):
        while True:
            msg = self.node.recv()
            self.log.recv(msg["from"], msg["clock"], msg["text"], msg["remaining"], self.clock)
            self.on_receive(msg)
            self.write_verse(msg)

    def on_receive(self, msg):
        # Merge: element-wise max. A REQUEST carries [0,0,0], so merging it changes nothing.
        self.clock = [max(mine, theirs) for mine, theirs in zip(self.clock, msg["clock"])]

    def write_verse(self, msg):
        prev = msg["prefix"] if msg["type"] == "REQUEST" else msg["text"]
        time.sleep(random.uniform(MIN_PROCESS, MAX_PROCESS))
        verse = next_verse(prev, self.name)
        remaining = msg["remaining"] - 1

        # Writing a verse is one event: tick my own entry once (both sends share this time).
        self.clock[self.me] += 1

        # TODO(you): which clock value goes on the outgoing messages? Is a plain reference to
        #   self.clock safe here, or does it need to be a copy?
        stamp = self.clock

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
