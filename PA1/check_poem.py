"""Check logs/poem.txt for causal consistency.

This checker MAY read verse contents (word counts) as ground truth, because it is only grading.
Your Poet must NOT do this. It must order verses using vector clocks alone.
"""

import re
import sys
from collections import defaultdict

LINE = re.compile(r"^(.*?)\s+\[([\d,\s]+)\]\s*$")


def leq(a, b):
    return all(x <= y for x, y in zip(a, b))


def lt(a, b):
    return leq(a, b) and a != b


def main(path="logs/poem.txt"):
    lines = []
    for raw in open(path):
        if raw.strip():
            m = LINE.match(raw.rstrip())
            lines.append((m.group(1), [int(x) for x in m.group(2).split(",")]))

    errors = []
    chains = defaultdict(list)  # prefix -> [(line_no, word_count, clock)]
    for i, (verse, clock) in enumerate(lines, 1):
        words = verse.split()
        chains[words[0]].append((i, len(words) - 1, clock))

    # 1. Ground truth: within a chain, verse k+1 was written after seeing verse k.
    for prefix, items in chains.items():
        counts = [c for _, c, _ in items]
        if counts != list(range(1, len(counts) + 1)):
            errors.append(f"{prefix}: verses out of order, word counts {counts}")
        # 2. Clocks along a chain must strictly increase (otherwise the clocks carry no information).
        for (i1, _, c1), (i2, _, c2) in zip(items, items[1:]):
            if not lt(c1, c2):
                errors.append(f"{prefix}: line {i1} {c1} should be < line {i2} {c2}")

    # 3. No line may appear after a line that happens-after it.
    for i in range(len(lines)):
        for j in range(i + 1, len(lines)):
            if lt(lines[j][1], lines[i][1]):
                errors.append(f"line {j+1} {lines[j][1]} happened-before line {i+1} {lines[i][1]} "
                              f"but was output later")

    print(f"{len(lines)} verses, chains: {', '.join(f'{p}={len(v)}' for p, v in chains.items())}")
    for e in errors:
        print("  FAIL:", e)
    print("PASS: causally consistent" if not errors else f"{len(errors)} problem(s)")
    return not errors


if __name__ == "__main__":
    sys.exit(0 if main(*sys.argv[1:]) else 1)
