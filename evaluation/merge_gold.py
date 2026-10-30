"""
Merge two labellers' files into labels_gold.csv by UNION: a tool is in the gold labels if either
labeller wrote it. Rationale: in our agreement check almost all disagreements were one labeller
missing a tool the other found, not two labellers disagreeing about the same mention.

    uv run python evaluation/merge_gold.py evaluation/labels_A.csv evaluation/labels_B.csv
    uv run python evaluation/evaluate.py --check evaluation/labels_gold.csv

Spellings of the same tool are merged first ("EC2" / "Amazon EC2", "Dialogflow" / "Google Dialogflow"),
using the same name mapping as evaluate.py plus vendor-prefix stripping for out-of-vocabulary tools.
Every tool only one labeller wrote is listed in `notes` ("only A: ..."), so the union stays traceable
and anything that breaks GUIDELINES.md can still be removed by hand afterwards.
"""
from __future__ import annotations

import argparse
import csv
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evaluation"))

from evaluate import ONET, OOV, LabelNormaliser, parse_tools  # noqa: E402
from skillradar.matcher import squash  # noqa: E402

VENDORS = ("amazon", "aws", "microsoft", "ms", "google", "apache", "ibm", "oracle")


def key(name: str, norm: LabelNormaliser) -> str:
    """One key per tool, so different spellings of the same tool collapse."""
    t = norm(name)
    words = name.lower().split()
    # evaluate.py reads "Google Dialogflow" as just the vendor ("Google"): don't trust a match on the vendor alone
    vendor_only = len(words) > 1 and words[0] in VENDORS and squash(t) == squash(words[0])
    if not t.startswith(OOV) and not vendor_only:
        return t
    while len(words) > 1 and words[0] in VENDORS:     # "Amazon EC2" -> "ec2"; a lone "Google" stays
        words = words[1:]
    k = squash(" ".join(words))
    # the vendor-less name may itself be in the vocabulary ("Google Dialogflow" -> "Dialogflow")
    t2 = norm(" ".join(words))
    return t2 if not t2.startswith(OOV) else OOV + k


def pick(spellings: list[str], norm: LabelNormaliser) -> str:
    """Prefer a spelling that maps into our vocabulary, then the shorter (vendor-less) one."""
    return sorted(spellings, key=lambda s: (key(s, norm).startswith(OOV) or norm(s) != key(s, norm),
                                            len(s), s.lower()))[0]


def merge(a: pd.DataFrame, b: pd.DataFrame, norm: LabelNormaliser, names: tuple[str, str]) -> list[dict]:
    rows = []
    b = b.set_index("item_id")
    for _, ra in a.iterrows():
        item = ra["item_id"]
        if item not in b.index:
            raise ValueError(f"{item} is in the first file but not the second")
        rb = b.loc[item]
        groups: dict[str, dict[str, list[str]]] = {}      # key -> {labeller: [spellings]}
        for who, cell in ((names[0], ra["true_tools"]), (names[1], rb["true_tools"])):
            for t in parse_tools(cell):
                groups.setdefault(key(t, norm), {}).setdefault(who, []).append(t)
        tools, only = [], {names[0]: [], names[1]: []}
        for g in groups.values():
            name = pick([s for v in g.values() for s in v], norm)
            tools.append(name)
            if len(g) == 1:
                only[next(iter(g))].append(name)
        notes = [n for n in (ra.get("notes", ""), rb.get("notes", "")) if str(n).strip()]
        notes = list(dict.fromkeys(notes))                # same note twice -> once
        for who, ts in only.items():
            if ts:
                notes.append(f"only {who}: {', '.join(ts)}")
        rows.append({"item_id": item, "split": ra["split"], "labeller": "+".join(names),
                     "true_tools": "; ".join(tools), "notes": "; ".join(notes)})
    return rows


def main(argv=None) -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("file_a")
    ap.add_argument("file_b")
    ap.add_argument("-o", "--out", default=str(ROOT / "evaluation" / "labels_gold.csv"))
    args = ap.parse_args(argv)
    read = lambda p: pd.read_csv(p, dtype=str, keep_default_na=False)
    a, b = read(args.file_a), read(args.file_b)
    who = lambda df, p: (df["labeller"].str.strip().iloc[0] if "labeller" in df and df["labeller"].str.strip().iloc[0]
                         else Path(p).stem.removeprefix("labels_"))
    names = (who(a, args.file_a), who(b, args.file_b))
    norm = LabelNormaliser(pd.read_csv(ONET))
    rows = merge(a, b, norm, names)
    with open(args.out, "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=["item_id", "split", "labeller", "true_tools", "notes"])
        w.writeheader()
        w.writerows(rows)
    n_only = sum(r["notes"].count("only ") for r in rows)
    print(f"wrote {args.out}: {len(rows)} items, union of {names[0]} and {names[1]} "
          f"({n_only} items have tools from one labeller only, listed in notes)")


if __name__ == "__main__":
    main()