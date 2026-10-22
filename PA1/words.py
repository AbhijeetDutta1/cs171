"""Verse generation. Each temperament draws random words from its own vocabulary."""

import random

WORDS = {
    "Happy": ["sunshine", "cheerful", "glow", "golden", "dancing", "free", "bright",
              "laughter", "summer", "bloom", "joy", "sparkle"],
    "Sad":   ["silent", "weary", "sorrow", "tears", "mourning", "grey", "dusk",
              "broken", "fading", "lonely", "rain", "hollow"],
    "Love":  ["forever", "beloved", "passion", "rose", "embrace", "tender", "heart",
              "devotion", "kiss", "longing", "darling", "warmth"],
}


def next_verse(prev, temperament):
    """Return a verse with one more word than prev.

    prev is either the previous verse ("FIRST glow") or, for a fresh request,
    just the prefix ("FIRST"). The prefix word is kept and not counted.
    """
    prefix, *body = prev.split()
    return " ".join([prefix] + random.choices(WORDS[temperament], k=len(body) + 1))
