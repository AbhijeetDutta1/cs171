# Shared configuration for all processes.

AGENTS = ["Happy", "Sad", "Love"]
INDEX = {name: i for i, name in enumerate(AGENTS)}   # position of each agent in a vector clock

HOST = "127.0.0.1"
PORTS = {"Poet": 6000, "Happy": 6001, "Sad": 6002, "Love": 6003}

# Every message is delayed by an independent random amount in [MIN_DELAY, MAX_DELAY] seconds.
MIN_DELAY, MAX_DELAY = 0.1, 1.5
# Simulated "thinking time" for an agent to write a verse.
MIN_PROCESS, MAX_PROCESS = 0.05, 0.3

LOG_DIR = "logs"
