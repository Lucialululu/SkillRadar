"""
Goal 1 evaluation: how well do our matchers find the tools a human labelled?

    # main result: all ablation steps on the held-out test items (postings + CVs)
    uv run python evaluation/evaluate.py evaluation/labels_gold.csv

    # one matcher, with every false positive / false negative listed (use on dev to find bugs)
    uv run python evaluation/evaluate.py evaluation/labels_gold.csv --split dev --matcher full --errors

    # later: any class with extract_tools(text) -> set[str], built as Class(software_df)
    uv run python evaluation/evaluate.py evaluation/labels_gold.csv --matcher full skillradar.llm_matcher:LLMMatcher

    # the method comparison: everything against the keyword matcher, paired on the same items
    uv run python evaluation/evaluate.py evaluation/labels_gold.csv --matcher full exact vendor acronym --baseline full

    # label files: which names could not be mapped onto O*NET? / agreement between two labellers
    uv run python evaluation/evaluate.py --check evaluation/labels_lucia.csv
    uv run python evaluation/evaluate.py --agreement evaluation/labels_A.csv evaluation/labels_B.csv

Metrics, all micro-averaged over (item, tool) pairs:
    precision       found tools that are in the labels / all found tools
    recall (vocab)  labelled tools we found / labelled tools that exist in our O*NET vocabulary
    recall (all)    labelled tools we found / ALL labelled tools (out-of-vocabulary ones count as missed)
    F1              harmonic mean of precision and recall (vocab)
95% intervals: bootstrap over items (2,000 resamples), because tools within one item are not independent.

Paired comparison (printed whenever more than one matcher is given): for each matcher vs the
baseline, the DIFFERENCE in F1 / precision / recall with a 95% interval, a bootstrap p-value and a
per-item count of where the matcher makes fewer / more errors. Both matchers are scored on the same
resampled items, so easy-vs-hard postings cancel out. Use this, not overlapping separate intervals,
to decide whether a method is better.
"""
from __future__ import annotations

import argparse
import importlib
import random
import sys
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from skillradar.cv_parser import read_cv  # noqa: E402
from skillradar.matcher import KeywordMatcher, squash  # noqa: E402
from skillradar.report import display_name  # noqa: E402
from skillradar.variants import STEPS, make_matcher  # noqa: E402

ONET = ROOT / "data" / "onet" / "software_skills.csv"
ITEMS = ROOT / "evaluation" / "items"
CVS = ROOT / "data" / "cvs"
OOV = "OOV:"          # prefix for labelled tools that are not in our vocabulary


# ---------------------------------------------------------------------------
# Labels
# ---------------------------------------------------------------------------

class LabelNormaliser:
    """Maps what a human wrote ("SQL", "power bi", "scikit-learn") onto an O*NET tool name.
    Uses all aliases, ignoring MANUAL_DROP: a labeller writing "Go" means the language."""

    def __init__(self, software: pd.DataFrame):
        self.m = KeywordMatcher(software, manual_drop=[])
        self.vocab = set(self.m.vocab)
        self.index = dict(self.m._squash_index())
        for tool in self.vocab:
            self.index.setdefault(squash(tool), tool)
            self.index.setdefault(squash(display_name(tool)), tool)

    def __call__(self, name: str) -> str:
        name = name.strip()
        tool = self.index.get(squash(name))
        if tool:
            return tool
        found = self.m.extract_tools(name)          # e.g. "Microsoft SQL Server 2019"
        return found.pop() if len(found) == 1 else OOV + name


def parse_tools(cell) -> list[str]:
    if not isinstance(cell, str):
        return []
    return [t.strip() for t in cell.replace(",", ";").split(";") if t.strip()]


def load_labels(path: Path, norm: LabelNormaliser) -> pd.DataFrame:
    df = pd.read_csv(path, dtype=str, keep_default_na=False)
    missing = {"item_id", "split", "true_tools"} - set(df.columns)
    if missing:
        raise ValueError(f"{path} lacks columns {missing}")
    df = df[df["labeller"].str.strip() != ""] if "labeller" in df else df
    df["truth"] = df["true_tools"].map(lambda c: {norm(t) for t in parse_tools(c)})
    df["side"] = df["item_id"].map(lambda i: "posting" if i.startswith("post_") else "cv")
    return df.reset_index(drop=True)


def item_text(item_id: str) -> str:
    p = ITEMS / f"{item_id}.txt"
    if p.exists():
        return p.read_text(encoding="utf-8")
    for ext in (".pdf", ".docx", ".txt", ".md"):
        if (CVS / f"{item_id}{ext}").exists():
            return read_cv(CVS / f"{item_id}{ext}")
    raise FileNotFoundError(f"no text for {item_id}: expected {p} or data/cvs/{item_id}.*")


# ---------------------------------------------------------------------------
# Metrics
# ---------------------------------------------------------------------------

@dataclass
class Counts:
    tp: int = 0
    fp: int = 0
    fn_vocab: int = 0
    fn_oov: int = 0

    def __add__(self, o):
        return Counts(self.tp + o.tp, self.fp + o.fp, self.fn_vocab + o.fn_vocab, self.fn_oov + o.fn_oov)

    @property
    def precision(self):
        return self.tp / (self.tp + self.fp) if self.tp + self.fp else float("nan")

    @property
    def recall_vocab(self):
        return self.tp / (self.tp + self.fn_vocab) if self.tp + self.fn_vocab else float("nan")

    @property
    def recall_all(self):
        d = self.tp + self.fn_vocab + self.fn_oov
        return self.tp / d if d else float("nan")

    @property
    def f1(self):
        p, r = self.precision, self.recall_vocab
        return 2 * p * r / (p + r) if p + r else float("nan")


def score_item(found: set[str], truth: set[str]) -> Counts:
    oov = {t for t in truth if t.startswith(OOV)}
    in_vocab = truth - oov
    return Counts(tp=len(found & in_vocab), fp=len(found - in_vocab),
                  fn_vocab=len(in_vocab - found), fn_oov=len(oov))


def total(counts: list[Counts]) -> Counts:
    out = Counts()
    for c in counts:
        out = out + c
    return out


def bootstrap_ci(counts: list[Counts], metric: str, n_boot: int = 2000, seed: int = 0) -> tuple[float, float]:
    if not counts:
        return (float("nan"), float("nan"))
    rng = random.Random(seed)
    vals = sorted(
        v for v in (getattr(total([rng.choice(counts) for _ in counts]), metric) for _ in range(n_boot))
        if v == v                                   # drop NaN
    )
    if not vals:
        return (float("nan"), float("nan"))
    return vals[int(0.025 * (len(vals) - 1))], vals[int(0.975 * (len(vals) - 1))]


@dataclass
class Paired:
    diff: float                 # metric(B) - metric(A) on the full item set
    lo: float                   # 95% bootstrap interval of the difference
    hi: float
    p: float                    # two-sided bootstrap p-value for "no difference"


def paired_bootstrap(a: list[Counts], b: list[Counts], metric: str = "f1",
                     n_boot: int = 2000, seed: int = 0) -> Paired:
    """Difference metric(B) - metric(A) for two matchers scored on the SAME items.

    Each resample draws item indices once and scores both matchers on that same draw,
    so 'this sample happened to contain many hard postings' cancels out. That makes
    the interval for the difference much narrower than comparing two separate intervals.
    """
    if len(a) != len(b):
        raise ValueError("paired comparison needs the same items for both matchers")
    nan = float("nan")
    if not a:
        return Paired(nan, nan, nan, nan)
    diff = getattr(total(b), metric) - getattr(total(a), metric)
    rng = random.Random(seed)
    n = len(a)
    diffs = []
    for _ in range(n_boot):
        idx = [rng.randrange(n) for _ in range(n)]
        d = getattr(total([b[i] for i in idx]), metric) - getattr(total([a[i] for i in idx]), metric)
        if d == d:                                  # drop NaN
            diffs.append(d)
    if not diffs:
        return Paired(diff, nan, nan, nan)
    diffs.sort()
    lo, hi = diffs[int(0.025 * (len(diffs) - 1))], diffs[int(0.975 * (len(diffs) - 1))]
    # share of resamples on the other side of zero, doubled (percentile bootstrap p-value)
    below = sum(d <= 0 for d in diffs) / len(diffs)
    above = sum(d >= 0 for d in diffs) / len(diffs)
    p = min(1.0, 2 * min(below, above))
    return Paired(diff, lo, hi, p)


def item_wins(a: list[Counts], b: list[Counts]) -> tuple[int, int, int]:
    """Per item: does B make fewer errors (false positives + in-vocabulary misses) than A?
    Returns (B better, B worse, tie). Easy to explain next to the bootstrap numbers."""
    err = lambda c: c.fp + c.fn_vocab
    better = sum(err(y) < err(x) for x, y in zip(a, b))
    worse = sum(err(y) > err(x) for x, y in zip(a, b))
    return better, worse, len(a) - better - worse


def kappa(a: list[bool], b: list[bool]) -> float:
    n = len(a)
    if n == 0:
        return float("nan")
    po = sum(x == y for x, y in zip(a, b)) / n
    pa, pb = sum(a) / n, sum(b) / n
    pe = pa * pb + (1 - pa) * (1 - pb)
    return (po - pe) / (1 - pe) if pe < 1 else float("nan")


# ---------------------------------------------------------------------------
# Matchers
# ---------------------------------------------------------------------------

def load_matcher(spec: str, software: pd.DataFrame):
    if spec in STEPS:
        return make_matcher(software, spec)
    if spec == "keyword":
        return make_matcher(software, "full")
    module, _, cls = spec.partition(":")
    return getattr(importlib.import_module(module), cls)(software)


# ---------------------------------------------------------------------------
# Commands
# ---------------------------------------------------------------------------

def md(df: pd.DataFrame) -> str:
    """DataFrame -> markdown table (paste-able into notes / the report draft)."""
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def fmt(x: float) -> str:
    return "–" if x != x else f"{x:.2f}"


def cmd_evaluate(args, software, norm):
    labels = load_labels(Path(args.labels), norm)
    if args.split != "all":
        labels = labels[labels["split"] == args.split]
    if labels.empty:
        raise SystemExit(f"no labelled items in split '{args.split}'")
    texts = {i: item_text(i) for i in labels["item_id"]}

    rows, details, scored = [], {}, {}
    # per-side rows only add information when the labels contain both postings and CVs
    sides = ["all", "posting", "cv"] if labels["side"].nunique() > 1 else ["all"]
    for spec in args.matcher:
        m = load_matcher(spec, software)
        per_item = {r.item_id: (m.extract_tools(texts[r.item_id]), r.truth, r.side) for r in labels.itertuples()}
        details[spec] = (m, per_item)
        for side in sides:
            cs = [score_item(f, t) for f, t, s in per_item.values() if side == "all" or s == side]
            scored[(spec, side)] = cs
            if not cs:
                continue
            c = total(cs)
            p_lo, p_hi = bootstrap_ci(cs, "precision", n_boot=args.n_boot)
            r_lo, r_hi = bootstrap_ci(cs, "recall_vocab", n_boot=args.n_boot)
            f_lo, f_hi = bootstrap_ci(cs, "f1", n_boot=args.n_boot)
            rows.append({
                "matcher": spec, "side": side, "items": len(cs),
                "precision": f"{fmt(c.precision)} ({fmt(p_lo)}–{fmt(p_hi)})",
                "recall (vocab)": f"{fmt(c.recall_vocab)} ({fmt(r_lo)}–{fmt(r_hi)})",
                "recall (all)": fmt(c.recall_all),
                "F1": f"{fmt(c.f1)} ({fmt(f_lo)}–{fmt(f_hi)})",
                "TP": c.tp, "FP": c.fp, "FN vocab": c.fn_vocab, "FN OOV": c.fn_oov,
            })

    n_truth = sum(len(t) for t in labels["truth"])
    n_oov = sum(1 for t in labels["truth"] for x in t if x.startswith(OOV))
    print(f"split={args.split} · {len(labels)} items "
          f"({(labels['side'] == 'posting').sum()} postings, {(labels['side'] == 'cv').sum()} CVs) · "
          f"{n_truth} labelled tools, {n_oov} out of vocabulary ({n_oov / max(n_truth, 1):.0%})\n")
    print(md(pd.DataFrame(rows)))

    # paired comparison: every other matcher against the baseline, on the same items
    baseline = args.baseline or args.matcher[0]
    if baseline not in args.matcher:
        raise SystemExit(f"--baseline {baseline!r} must be one of the matchers in --matcher")
    others = [s for s in args.matcher if s != baseline]
    if others:
        sd = lambda d: f"{d.diff:+.2f} ({d.lo:+.2f} to {d.hi:+.2f})" if d.diff == d.diff else "–"
        prow = []
        for spec in others:
            for side in sides:
                a, b = scored[(baseline, side)], scored[(spec, side)]
                if not a:
                    continue
                f = paired_bootstrap(a, b, "f1", args.n_boot)
                pr = paired_bootstrap(a, b, "precision", args.n_boot)
                rc = paired_bootstrap(a, b, "recall_vocab", args.n_boot)
                better, worse, tie = item_wins(a, b)
                prow.append({
                    "compared": f"{spec} − {baseline}", "side": side, "items": len(a),
                    "ΔF1 (95% CI)": sd(f), "p": "–" if f.p != f.p else f"{f.p:.3f}",
                    "Δprecision": sd(pr), "Δrecall (vocab)": sd(rc),
                    "items better / worse / same": f"{better} / {worse} / {tie}",
                })
        print(f"\nPaired comparison against '{baseline}' (bootstrap over items, both matchers scored on the "
              f"same resample; an interval that excludes 0 means a real difference on this kind of data)\n")
        print(md(pd.DataFrame(prow)))

    if args.errors:
        for spec, (m, per_item) in details.items():
            print(f"\n## Errors for {spec}")
            for item, (found, truth, _) in per_item.items():
                fp = found - truth
                fn = {t for t in truth if t not in found}
                if not fp and not fn:
                    continue
                fired = {}
                if hasattr(m, "explain"):
                    for alias, tool in m.explain(texts[item]).items():
                        fired.setdefault(tool, alias)
                print(f"{item}:")
                if fp:
                    print("  false positive: " + ", ".join(
                        f"{display_name(t)} (fired on {fired.get(t, '?')!r})" for t in sorted(fp)))
                if fn:
                    print("  missed: " + ", ".join(
                        t[len(OOV):] + " [not in vocab]" if t.startswith(OOV) else display_name(t)
                        for t in sorted(fn)))


def cmd_check(path, norm):
    labels = pd.read_csv(path, dtype=str, keep_default_na=False)
    names = sorted({t for c in labels["true_tools"] for t in parse_tools(c)}, key=str.lower)
    rows = [{"you wrote": n, "maps to": norm(n)} for n in names]
    df = pd.DataFrame(rows)
    oov = df["maps to"].str.startswith(OOV)
    print(md(df[~oov]))
    print(f"\nNot in our vocabulary ({oov.sum()}): fix typos, keep real out-of-vocabulary tools as they are")
    print(", ".join(df.loc[oov, "you wrote"]) or "none")
    empty = labels[(labels["labeller"].str.strip() != "") & (labels["true_tools"].str.strip() == "")]
    if len(empty):
        print(f"\nItems with a labeller but no tools (fine if the text really has none): {', '.join(empty['item_id'])}")


def cmd_agreement(path_a, path_b, norm):
    a, b = load_labels(Path(path_a), norm), load_labels(Path(path_b), norm)
    both = a.merge(b, on="item_id", suffixes=("_a", "_b"))
    if both.empty:
        raise SystemExit("no items labelled in both files")
    inter = sum(len(x & y) for x, y in zip(both["truth_a"], both["truth_b"]))
    size = sum(len(x) + len(y) for x, y in zip(both["truth_a"], both["truth_b"]))
    pos_agree = 2 * inter / size if size else float("nan")

    vocab = sorted(norm.vocab)
    ka, kb = [], []
    for x, y in zip(both["truth_a"], both["truth_b"]):
        ka += [t in x for t in vocab]
        kb += [t in y for t in vocab]
    print(f"{len(both)} items labelled by both")
    print(f"positive agreement (F1 between labellers): {pos_agree:.2f}")
    print(f"Cohen's kappa over item x vocabulary decisions: {kappa(ka, kb):.2f} "
          "(inflated by the many easy 'not mentioned' decisions; report F1 first)")
    print("\nDisagreements (discuss, then write labels_gold.csv):")
    for r in both.itertuples():
        only_a, only_b = r.truth_a - r.truth_b, r.truth_b - r.truth_a
        if only_a or only_b:
            show = lambda s: ", ".join(sorted(t[len(OOV):] if t.startswith(OOV) else display_name(t) for t in s))
            print(f"  {r.item_id}: only A: {show(only_a) or '-'} | only B: {show(only_b) or '-'}")


def main(argv=None):
    ap = argparse.ArgumentParser(description="Goal 1 evaluation (see module docstring)")
    ap.add_argument("labels", nargs="?", help="label file, normally evaluation/labels_gold.csv")
    ap.add_argument("--matcher", nargs="+", default=STEPS,
                    help=f"any of {STEPS}, 'keyword', or module:Class (default: the 4 ablation steps)")
    ap.add_argument("--baseline", help="matcher the others are compared against (default: the first in --matcher)")
    ap.add_argument("--n-boot", type=int, default=2000, help="bootstrap resamples (default 2000)")
    ap.add_argument("--split", choices=["test", "dev", "all"], default="test")
    ap.add_argument("--errors", action="store_true", help="list false positives / misses per item")
    ap.add_argument("--check", metavar="LABELS", help="show how label names map onto O*NET")
    ap.add_argument("--agreement", nargs=2, metavar=("A", "B"), help="agreement between two label files")
    args = ap.parse_args(argv)

    software = pd.read_csv(ONET)
    norm = LabelNormaliser(software)
    if args.check:
        cmd_check(args.check, norm)
    elif args.agreement:
        cmd_agreement(*args.agreement, norm)
    elif args.labels:
        cmd_evaluate(args, software, norm)
    else:
        ap.error("give a label file, --check or --agreement")


if __name__ == "__main__":
    main()
