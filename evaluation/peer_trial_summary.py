"""Goal 3 summary: facilitator CSV + questionnaire export -> numbers for the paper.

Usage:
    uv run python evaluation/peer_trial_summary.py data/user_study/sheet_export.csv

Facilitator record: evaluation/peer_trial_results.csv (one row per participant, task codes
no_help / with_help / failed). Questionnaire: the Google Sheet exported as CSV (gitignored).
Rows are joined on participant_id; practice rows (test_run = True) and pilot codes P01-P02 are left out.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

HERE = Path(__file__).parent
FACILITATOR = HERE / "peer_trial_results.csv"
TASKS = ["task1_upload_role", "task2_correct_tools", "task3_understand_report", "task4_choose_tool"]
CODES = ["no_help", "with_help", "failed"]
QUESTIONS = ["accuracy", "relevance", "usefulness", "explanation", "trust", "ease_of_use"]
PILOT = {"P01", "P02"}


def load_facilitator(path: Path = FACILITATOR) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"participant_id": str})
    df = df[df["consent"].astype(str).str.lower().eq("yes")]          # empty template rows drop out here
    df = df[~df["participant_id"].isin(PILOT)]
    bad = {c: sorted(set(df[c].dropna()) - set(CODES)) for c in TASKS}
    bad = {c: v for c, v in bad.items() if v}
    if bad:
        raise ValueError(f"Unknown task codes (use {CODES}): {bad}")
    return df


def load_sheet(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"participant_id": str})
    df = df[~df["test_run"].astype(str).str.lower().eq("true")]
    df = df[~df["participant_id"].isin(PILOT)]
    return df.drop_duplicates("participant_id", keep="last")


def summarise(fac: pd.DataFrame, sheet: pd.DataFrame | None) -> str:
    n = len(fac)
    out = [f"Peer trial: {n} participants (facilitator record)"]
    if n == 0:
        return out[0]
    if "app_version" in fac and fac["app_version"].nunique() > 1:
        out.append(f"WARNING: several app versions: {sorted(fac['app_version'].dropna().unique())}")

    out += ["", "Task success", "| task | without help | with help | failed |", "|---|---|---|---|"]
    for t in TASKS:
        c = fac[t].value_counts()
        out.append(f"| {t} | {c.get('no_help', 0)}/{n} | {c.get('with_help', 0)}/{n} | {c.get('failed', 0)}/{n} |")

    num = fac[["tools_initial", "tools_removed", "tools_added", "missing_shown", "missing_agreed"]].apply(
        pd.to_numeric, errors="coerce")
    init, rem, add = num["tools_initial"].sum(), num["tools_removed"].sum(), num["tools_added"].sum()
    out += ["", "Correction (Goal 1 in real use)",
            f"- tools found: {init:.0f}; removed (false positives): {rem:.0f} ({rem / init:.0%}); "
            f"added (misses): {add:.0f} ({add / init:.0%} of found)" if init else "- no tool counts",
            f"- participants who changed nothing: {int(((num['tools_removed'] == 0) & (num['tools_added'] == 0)).sum())}/{n}"]
    shown, agreed = num["missing_shown"].sum(), num["missing_agreed"].sum()
    if shown:
        out.append(f"- perceived accuracy: {agreed:.0f} of {shown:.0f} missing tools agreed to be missing ({agreed / shown:.0%})")

    if sheet is not None:
        q = sheet[sheet["participant_id"].isin(fac["participant_id"])]
        missing = sorted(set(fac["participant_id"]) - set(q["participant_id"]))
        out += ["", f"Questionnaire (1-5, n = {len(q)})"]
        if missing:
            out.append(f"WARNING: no questionnaire row for {missing}")
        out += ["| statement | median | min-max | share 4-5 |", "|---|---|---|---|"]
        for col in QUESTIONS:
            v = pd.to_numeric(q[col], errors="coerce").dropna()
            if len(v):
                out.append(f"| {col} | {v.median():g} | {v.min():g}-{v.max():g} | {(v >= 4).mean():.0%} |")
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", nargs="?", type=Path, help="questionnaire export (CSV); optional")
    ap.add_argument("--facilitator", type=Path, default=FACILITATOR)
    a = ap.parse_args()
    print(summarise(load_facilitator(a.facilitator), load_sheet(a.sheet) if a.sheet else None))


if __name__ == "__main__":
    main()
