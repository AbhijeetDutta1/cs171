"""Launch the 3 agents + Poet as separate processes, then check the poem.

  python3 run.py 1            part 1: one request
  python3 run.py 2            part 2: three concurrent requests
  python3 run.py 2 --n 4 4 4  custom verse counts
"""

import subprocess
import sys
import time

from config import AGENTS

py = sys.executable
agents = [subprocess.Popen([py, "agent.py", name]) for name in AGENTS]
time.sleep(0.5)  # let agents start listening
try:
    subprocess.run([py, "poet.py", *sys.argv[1:]])
finally:
    for a in agents:
        a.terminate()
    for a in agents:
        a.wait()

print("\n" + "=" * 60, flush=True)
subprocess.run([py, "check_poem.py"])
