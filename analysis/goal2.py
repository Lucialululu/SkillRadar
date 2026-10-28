"""
Goal 2 analysis: robust current demand + entry level vs senior. Prints markdown tables
(paste them into notes / the report) and saves CSVs + figures to analysis/results/.

Needs only the small tables from `main.py build` (both sources):
    uv run python analysis/goal2.py
    uv run python analysis/goal2.py --top 20 --boot 1000 --roles "data scientist" "software engineer"

Comparisons
  A  replication, all levels   : primary (US only, Jan 2024) vs secondary (US, Apr 2024)
  B  replication, levels matched: same, but secondary restricted to mid-senior + associate,
                                  because the primary dataset has no entry-level postings
  C  rank stability             : bootstrap rank intervals in the primary dataset (what the app uses)
  D  entry vs senior            : secondary only (the only dataset with entry/internship postings)
"""
from __future__ import annotations

import argparse
import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))

from skillradar.demand import ROLE_PATTERNS, filter_postings, load_posting_tools  # noqa: E402
from skillradar.report import display_name  # noqa: E402
from skillradar.robustness import rank_intervals, replication, seniority  # noqa: E402

OUT = ROOT / "analysis" / "results"
PRIMARY_LEVELS = ["mid-senior", "associate"]


def md(df: pd.DataFrame) -> str:
    cols = [str(c) for c in df.columns]
    lines = ["| " + " | ".join(cols) + " |", "|" + "---|" * len(cols)]
    lines += ["| " + " | ".join(str(v) for v in row) + " |" for row in df.itertuples(index=False)]
    return "\n".join(lines)


def pct(x) -> str:
    return f"{x * 100:.1f}"


def scatter(rep, path: Path, title: str) -> None:
    import matplotlib
    matplotlib.use("Agg")
    import matplotlib.pyplot as plt

    t = rep.table
    fig, ax = plt.subplots(figsize=(5, 5))
    m = max(t["share_a"].max(), t["share_b"].max()) * 100 * 1.08
    ax.plot([0, m], [0, m], color="#999", lw=1, ls="--", zorder=0)
    ax.scatter(t["share_a"] * 100, t["share_b"] * 100, s=18, color="#2b6cb0")
    for _, r in t.head(12).iterrows():
        ax.annotate(display_name(r["tool"]), (r["share_a"] * 100, r["share_b"] * 100),
                    fontsize=7, xytext=(3, 2), textcoords="offset points")
    ax.set_xlim(0, m), ax.set_ylim(0, m)
    ax.set_xlabel(f"% of postings, primary Jan 2024 (n={rep.n_a:,})")
    ax.set_ylabel(f"% of postings, secondary Apr 2024 (n={rep.n_b:,})")
    ax.set_title(f"{title}\nSpearman ρ = {rep.rho:.2f} (95% CI {rep.ci[0]:.2f}–{rep.ci[1]:.2f})", fontsize=9)
    fig.tight_layout()
    fig.savefig(path, dpi=200)
    plt.close(fig)


def main(argv=None):
    ap = argparse.ArgumentParser(description="Goal 2 analysis")
    ap.add_argument("--roles", nargs="+", default=list(ROLE_PATTERNS))
    ap.add_argument("--top", type=int, default=20)
    ap.add_argument("--boot", type=int, default=1000)
    ap.add_argument("--no-plots", action="store_true")
    args = ap.parse_args(argv)

    a, b = load_posting_tools("primary"), load_posting_tools("secondary")
    OUT.mkdir(parents=True, exist_ok=True)
    print(f"Duplicate ads removed (same text within a role): primary {a.attrs['n_duplicates']:,}, "
          f"secondary {b.attrs['n_duplicates']:,}\n")

    # ---- A + B: replication ------------------------------------------------
    summary = []
    for role in args.roles:
        for label, lv_b in [("A all levels", None), ("B levels matched", PRIMARY_LEVELS)]:
            r = replication(a, b, role, top=args.top, country_a="United States", levels_b=lv_b, n_boot=args.boot)
            summary.append({
                "role": role, "comparison": label, "n primary (US)": f"{r.n_a:,}", "n secondary": f"{r.n_b:,}",
                "tools compared": len(r.table), "Spearman ρ": f"{r.rho:.2f}",
                "95% CI": f"{r.ci[0]:.2f}–{r.ci[1]:.2f}", "note": "no postings" if min(r.n_a, r.n_b) == 0 else ("small sample" if r.small_sample else ""),
            })
            if label.startswith("A") and len(r.table):
                t = r.table.assign(tool=r.table["tool"].map(display_name))
                t.to_csv(OUT / f"replication_{role.replace(' ', '_')}.csv", index=False)
                if not args.no_plots:
                    scatter(r, OUT / f"replication_{role.replace(' ', '_')}.png", role)
    print(f"## A/B  Replication across datasets (top-{args.top} of each, union)\n")
    print(md(pd.DataFrame(summary)))

    # ---- C: rank stability -------------------------------------------------
    print(f"\n## C  Rank stability in the primary dataset (bootstrap 95% rank interval)\n")
    for role in args.roles:
        ri = rank_intervals(a, role, top=min(args.top, 15), n_boot=args.boot)
        if ri.empty:
            continue
        ri.to_csv(OUT / f"ranks_{role.replace(' ', '_')}.csv", index=False)
        show = pd.DataFrame({
            "rank": ri["rank"], "tool": ri["tool"].map(display_name), "% postings": ri["share"].map(pct),
            "rank 95% interval": [f"{lo}–{hi}" for lo, hi in zip(ri["rank_lo"], ri["rank_hi"])],
        })
        print(f"### {role} (n={ri.attrs['n_postings']:,})\n\n{md(show)}\n")

    # ---- D: entry vs senior ------------------------------------------------
    print("## D  Entry level + internship vs mid-senior (secondary dataset, BH-corrected q < 0.05)\n")
    for role in args.roles:
        s = seniority(b, role, top=args.top)
        nj, ns = s.attrs["n_junior"], s.attrs["n_senior"]
        if s.empty:
            print(f"### {role}: not enough postings (junior {nj}, senior {ns})\n")
            continue
        s.to_csv(OUT / f"seniority_{role.replace(' ', '_')}.csv", index=False)
        warn = "  ⚠ small sample, read as indicative only" if min(nj, ns) < 100 else ""
        mean_tools = lambda lv: filter_postings(b, role, lv)["tool_set"].map(len).mean()
        verbosity = (f"Tools per posting: junior {mean_tools(['entry', 'internship']):.1f}, "
                     f"senior {mean_tools(['mid-senior']):.1f} (longer ads list more tools, so read "
                     "small differences with care)")
        show = pd.DataFrame({
            "tool": s["tool"].map(display_name),
            "% junior": s["share_junior"].map(pct), "% senior": s["share_senior"].map(pct),
            "senior − junior (pp)": [f"{d:+.1f} ({lo:+.1f} to {hi:+.1f})"
                                     for d, lo, hi in zip(s["diff_pp"], s["ci_low_pp"], s["ci_high_pp"])],
            "q": s["q"].map(lambda q: f"{q:.3f}"), "sig.": s["significant"].map({True: "yes", False: ""}),
        })
        print(f"### {role} (junior n={nj:,}, senior n={ns:,}){warn}\n\n{verbosity}\n\n{md(show)}\n")

    print(f"CSVs{'' if args.no_plots else ' and figures'} saved in {OUT.relative_to(ROOT)}/")


if __name__ == "__main__":
    main()
