"""
Evidence for MANUAL_DROP: show where a suspicious alias fires in real postings.

A human reads the snippets and decides per alias:
  * mostly the tool  -> keep
  * mostly English / a company name -> add to MANUAL_DROP in skillradar/matcher.py,
    add a test case, rebuild both datasets.
This script never changes the matcher itself.

Run from the repo root (needs data/, reads the raw posting text):
    uv run python scripts/alias_snippets.py                       # Google Facebook C Go, both datasets
    uv run python scripts/alias_snippets.py Google Go --n 15 --source secondary
    uv run python scripts/alias_snippets.py Go > evaluation/alias_go.txt
"""
from __future__ import annotations

import argparse
import random
import re

import pandas as pd

from skillradar.demand import PROCESSED, SOURCES
from skillradar.matcher import KeywordMatcher, tokens

ONET = "data/onet/software_skills.csv"
DEFAULT = ["Google", "Facebook", "C", "Go"]
WINDOW = 90       # characters of context on each side


def find_snippets(text: str, alias: str, case_sensitive: bool, window: int = WINDOW) -> list[str]:
    """All places where alias occurs as a whole token sequence, with context.
    Uses the matcher's tokeniser rules, so 'C' does not fire inside 'C++' or 'C#'."""
    if not isinstance(text, str):
        return []
    # a match must not be glued to other token characters (same idea as matcher.TOKEN)
    pattern = r"(?<![A-Za-z0-9+#&])" + r"\s+".join(map(re.escape, tokens(alias))) + r"(?![A-Za-z0-9+#&])"
    # matcher.TOKEN also keeps "Node.js"-style tokens together: "Go." at sentence end is still "Go"
    out = []
    for m in re.finditer(pattern, text, flags=0 if case_sensitive else re.I):
        nxt, prv = text[m.end():m.end() + 2], text[max(0, m.start() - 2):m.start()]
        if re.match(r"[.-][A-Za-z0-9+#&]", nxt) or re.fullmatch(r"[A-Za-z0-9+#&][.-]", prv):
            continue                                # "Go-to", "C.V.", "Objective-C": a different token
        s, e = max(0, m.start() - window), min(len(text), m.end() + window)
        snip = text[s:e].replace("\n", " ")
        out.append(f"...{snip[:m.start() - s]}[[{m.group(0)}]]{snip[m.end() - s:]}...")
    return out


def posting_ids_with(tool: str, source: str, k: int, seed: int) -> list:
    pt = pd.read_csv(PROCESSED / f"posting_tools_{source}.csv", keep_default_na=False)
    ids = pt.loc[pt["tools"].str.split(";").map(lambda ts: tool in ts), "posting_id"].tolist()
    random.Random(seed).shuffle(ids)
    return ids[:k]


def texts_primary(ids: set) -> dict:
    out = {}
    for chunk in pd.read_csv(SOURCES["primary"] / "job_summary.csv", chunksize=100_000):
        hit = chunk[chunk["job_link"].isin(ids)]
        out.update(zip(hit["job_link"], hit["job_summary"]))
        if len(out) >= len(ids):
            break
    return out


def texts_secondary(ids: set) -> dict:
    p = pd.read_csv(SOURCES["secondary"] / "postings.csv", usecols=["job_id", "description", "skills_desc"])
    p = p[p["job_id"].isin(ids)]
    return dict(zip(p["job_id"], p["description"].fillna("") + "\n" + p["skills_desc"].fillna("")))


def main(argv=None):
    ap = argparse.ArgumentParser(description=__doc__.split("\n")[1])
    ap.add_argument("aliases", nargs="*", default=DEFAULT)
    ap.add_argument("--source", choices=["primary", "secondary", "both"], default="both")
    ap.add_argument("--n", type=int, default=10, help="snippets per alias and source")
    ap.add_argument("--seed", type=int, default=0)
    args = ap.parse_args(argv)

    m = KeywordMatcher.from_csv(ONET)
    sources = ["primary", "secondary"] if args.source == "both" else [args.source]
    for alias in args.aliases:
        key = next((k for k in m.alias_to_tool if k == alias), None) or \
              next((k for k in m.alias_to_tool if k.lower() == alias.lower()), None)
        if key is None:
            print(f"\n### {alias}: not an alias in the current matcher (already dropped?)")
            continue
        tool = m.alias_to_tool[key]
        case_sensitive = key != key.lower()
        for source in sources:
            ids = posting_ids_with(tool, source, k=args.n * 3, seed=args.seed)
            texts = (texts_primary if source == "primary" else texts_secondary)(set(ids))
            print(f"\n### alias {key!r} -> tool {tool!r} · {source} · "
                  f"{'case-sensitive' if case_sensitive else 'case-insensitive'}")
            shown = 0
            for pid in ids:
                snips = find_snippets(texts.get(pid, ""), key, case_sensitive)
                if snips:
                    shown += 1
                    print(f"{shown:2}. {snips[0]}")
                if shown >= args.n:
                    break
            if shown == 0:
                print("   no postings found")
        print(f"\nDecision for {key!r}: tool / English word / company name?  -> keep or MANUAL_DROP")


if __name__ == "__main__":
    main()
