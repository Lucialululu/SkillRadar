"""
Ablation variants of the keyword matcher (Goal 1 test): how much does each
normalisation step add? Each step is cumulative:

    exact    O*NET names only ("Structured query language SQL"), case-insensitive
    vendor   + drop "software" / vendor names ("Power BI", "Salesforce")
    acronym  + acronyms that abbreviate the name ("SQL", "AWS")
    full     + case-sensitive short names (R, Go, Excel, Spark) = KeywordMatcher

All variants use the same vocabulary and MANUAL_DROP, and expose the same
extract_tools(text) -> set[str], so evaluation/evaluate.py can swap them.

    from skillradar.variants import make_matcher
    m = make_matcher(software, "vendor")
"""
from __future__ import annotations

import re
from typing import Iterable

import pandas as pd

from skillradar.matcher import (
    KEEP, MANUAL_DROP, MAX_NGRAM, NO_SHORT, VENDORS, KeywordMatcher, alias_key, aliases,
    build_vocab, is_abbrev, tokens,
)

STEPS = ["exact", "vendor", "acronym", "full"]


def aliases_upto(name: str, step: str) -> set[str]:
    """The aliases a tool gets when only the normalisation steps up to `step` are on."""
    if step in ("acronym", "full"):
        return aliases(name)
    out = {name}
    if step == "vendor":
        out.add(KEEP.get(name, name))
        core = re.sub(r"\s+software$", "", name, flags=re.I)
        out.add(core)
        for v in VENDORS:
            if core.startswith(v + " ") and core[len(v) + 1:].lower() not in NO_SHORT:
                out.add(core[len(v) + 1:])
    return out


class VariantMatcher(KeywordMatcher):
    """KeywordMatcher with only some normalisation steps switched on."""

    def __init__(self, software: pd.DataFrame, step: str, manual_drop: Iterable[str] | None = None):
        if step not in STEPS:
            raise ValueError(f"step must be one of {STEPS}")
        self.step = step
        self.vocab, popularity = build_vocab(software)
        self.alias_to_tool = {}
        for tool in sorted(self.vocab, key=lambda t: popularity.get(t, 0)):
            for a in aliases_upto(tool, step):
                if tokens(a):
                    key = alias_key(a) if step == "full" else " ".join(tokens(a)).lower()
                    self.alias_to_tool[key] = tool
        self._squash_cache = None
        self.dropped = set()
        for a in (MANUAL_DROP if manual_drop is None else set(manual_drop)):
            self.drop(a)
        self.max_n = min(max(len(k.split()) for k in self.alias_to_tool), MAX_NGRAM)

    def __repr__(self) -> str:
        return f"VariantMatcher({self.step}, {len(self.vocab)} tools, {len(self.alias_to_tool)} aliases)"


def make_matcher(software: pd.DataFrame, step: str = "full", **kwargs) -> KeywordMatcher:
    return KeywordMatcher(software, **kwargs) if step == "full" else VariantMatcher(software, step, **kwargs)


__all__ = ["STEPS", "aliases_upto", "VariantMatcher", "make_matcher", "is_abbrev"]
