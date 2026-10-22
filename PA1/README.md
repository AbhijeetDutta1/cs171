# PA1: Causally Consistent Poems

```
python3 run.py 1              # Part 1: one request (FIRST) to a random agent
python3 run.py 2              # Part 2: FIRST->Happy, SECOND->Sad, THIRD->Love at the same time
python3 run.py 2 --n 4 5 6    # custom verse counts
python3 check_poem.py         # re-check logs/poem.txt
```

Outputs go to `logs/`: `poet.log`, `happy.log`, `sad.log`, `love.log`, `poem.txt`.

## Who wrote what

| File | What it does | Yours? |
|---|---|---|
| `config.py` | names, ports, delay ranges | provided |
| `net.py` | TCP sockets, random delays, inbox queue | provided |
| `words.py` | verse generation (random words from a temperament vocabulary) | provided |
| `logger.py` | log format matching the sample | provided |
| `run.py` | starts the 4 processes, then runs the checker | provided |
| `check_poem.py` | grades `poem.txt` (it may use word counts; your Poet must not) | provided |
| `agent.py` | **vector clock: init, receive rule, event rule, message stamp** | **TODO** |
| `poet.py` | **vector clock, causal delivery condition, hold-back queue** | **TODO** |

Search for `TODO(you)`. There are 7 of them. The placeholders run as-is, so run first and watch it fail.

## Suggested path

1. `python3 run.py 2`. Every clock shows `[0,0,0]`, and the checker fails.
2. Do the **agent** TODOs. Run again. The clocks along each chain should now go up, but the
   Poet still prints verses in arrival order, so you'll usually see "happened-before ... output later"
   failures. (Run it a few times: sometimes you get lucky.)
3. Do the **poet** TODOs. Run each mode about 10 times. Look for `held=True` lines in `poet.log`.
   Those are verses your hold-back queue saved.

If the Poet prints `STUCK`, your delivery condition is holding something it never releases.
The message tells you which verses are stuck and the Poet's clock at that point.

## Hints (read only as far as you need)

<details><summary>Hint 1: clock shape</summary>

The sample uses 3 entries `[Happy, Sad, Love]`, and the Poet's requests carry `[0,0,0]`. The only
events that matter for ordering are verses, and only agents write verses.
</details>

<details><summary>Hint 2: the agent rules</summary>

These are the standard vector clock rules. On receive, merge (element-wise max). On an event,
increment your own entry. The two sends share one vector time, so increment once, not once per send.
</details>

<details><summary>Hint 3: when may the Poet output a verse from agent j?</summary>

Two conditions:
(a) it is the *next* verse from j that the Poet hasn't seen yet, and
(b) the Poet has already output everything from the *other* agents that this verse depends on.
Write each one as a comparison between `msg["clock"]` and `self.clock`.
This is the same idea as causal broadcast (Birman–Schiper–Stephenson).
</details>

<details><summary>Hint 4: the hold-back loop</summary>

Delivering one held verse can unblock another, which can unblock a third. Keep sweeping until
a full pass delivers nothing.
</details>

## Questions to be ready for in the demo

- Why can't the Poet use word counts to order verses? What *would* break if two chains shared a prefix?
- Why does the agent's outgoing message need a *copy* of its clock?
- Does `net.py` give you FIFO channels? Would your solution still be correct if it did? Would you still need vector clocks?
- Why don't the Poet's requests need to increment anything?
- Point to two verses in your poem that are concurrent. How can you tell from their clocks?
- What changes if you add a 4th agent? (Expect to be asked to change something like this live.)
- What happens if a message is lost?
