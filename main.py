"""
SkillRadar command line.

    # once (slow, streams the big job-posting files), and again after matcher changes
    python main.py build --source primary
    python main.py build --source secondary

    # the tracer bullet: CV + role -> skill-gap report
    python main.py report my_cv.pdf "data scientist"
    python main.py report my_cv.pdf "data scientist" --source secondary --level entry internship
    python main.py report my_cv.pdf "data scientist" --explain     # which words matched which tool
"""
import argparse
import sys
import time

import pandas as pd

from skillradar.cv_parser import read_cv
from skillradar.demand import (
    LEVEL_MAP, ROLE_PATTERNS, build, demand_table, load_posting_tools, resolve_role,
)
from skillradar.matcher import KeywordMatcher
from skillradar.report import build_report, display_name, format_report

ONET = "data/onet/software_skills.csv"
SOURCE_NOTE = {"primary": "LinkedIn Jan 2024", "secondary": "LinkedIn Apr 2024, US"}


def cmd_build(args):
    matcher = KeywordMatcher.from_csv(ONET)
    print(f"{matcher}\nBuilding posting tools for '{args.source}' ...")
    t0 = time.time()
    path = build(args.source, matcher)
    df = pd.read_csv(path)
    print(f"Saved {len(df):,} postings to {path} in {time.time() - t0:.0f}s")
    print(df.groupby("role").size().rename("postings").to_string())


def cmd_report(args):
    role = resolve_role(args.role)
    if args.source == "primary" and args.level and set(args.level) & {"entry", "internship"}:
        raise ValueError("the primary dataset has no entry/internship postings, use --source secondary")
    matcher = KeywordMatcher.from_csv(ONET)
    cv_text = read_cv(args.cv)

    if args.show_text:
        print("----- extracted CV text -----\n" + cv_text + "\n-----------------------------\n")
    if args.explain:
        print("Matched in CV (alias -> tool):")
        for alias, tool in sorted(matcher.explain(cv_text).items(), key=lambda x: x[1]):
            print(f"  {alias!r:<25} -> {display_name(tool)}")
        print()

    cv_tools = matcher.extract_tools(cv_text)
    pt = load_posting_tools(args.source)
    software = pd.read_csv(ONET)
    demand = demand_table(pt, role, levels=args.level, country=args.country, software=software)

    note = SOURCE_NOTE[args.source]
    if args.level:
        note += ", levels: " + "/".join(args.level)
    if args.country:
        note += f", {args.country}"
    rep = build_report(cv_tools, demand, top=args.top, min_share=args.min_share, note=note)
    print(format_report(rep))


def main(argv=None):
    ap = argparse.ArgumentParser(description="SkillRadar: CV -> skill-gap report")
    sub = ap.add_subparsers(dest="cmd", required=True)

    b = sub.add_parser("build", help="precompute posting -> tools table from the raw data")
    b.add_argument("--source", choices=["primary", "secondary"], default="primary")
    b.set_defaults(func=cmd_build)

    r = sub.add_parser("report", help="skill-gap report for a CV")
    r.add_argument("cv", help="path to CV (.pdf, .docx, .txt, .md)")
    r.add_argument("role", help=f"target role, one of: {', '.join(ROLE_PATTERNS)}")
    r.add_argument("--source", choices=["primary", "secondary"], default="primary")
    r.add_argument("--level", nargs="+", choices=sorted(set(LEVEL_MAP.values())),
                   help="only these experience levels (entry/internship exist in 'secondary' only)")
    r.add_argument("--country", help="e.g. 'United States', 'United Kingdom' (primary only)")
    r.add_argument("--top", type=int, default=15, help="compare against the N most-demanded tools")
    r.add_argument("--min-share", type=float, default=0.05, help="ignore tools below this share")
    r.add_argument("--explain", action="store_true", help="show which words matched which tool")
    r.add_argument("--show-text", action="store_true", help="print the text extracted from the CV")
    r.set_defaults(func=cmd_report)

    args = ap.parse_args(argv)
    try:
        args.func(args)
    except (FileNotFoundError, ValueError) as e:
        sys.exit(f"error: {e}")


if __name__ == "__main__":
    main()
