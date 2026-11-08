"""Goal 3 summary: the study sheet -> numbers for the paper.

Usage:
    uv run python evaluation/peer_trial_summary.py data/user_study/sheet_export.csv

The input is the Google Sheet exported as CSV (File -> Download -> CSV; keep it in data/, which is gitignored),
or data/user_study/responses.csv when the app ran locally. Everything comes from the testing app's step 5:
the participant's ratings and 'not really missing' answer, and the facilitator's task codes and notes.
Practice rows (test_run = True) and the pilot codes are left out.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

TASKS = {"task1_upload_role": "1 upload + role", "task2_correct_tools": "2 check tools",
         "task3_understand_report": "3 explain report", "task4_choose_tool": "4 choose a tool"}
QUESTIONS = ["accuracy", "relevance", "usefulness", "explanation", "trust", "ease_of_use"]
PILOT = {"P01", "P02"}


def load(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path, dtype={"participant_id": str}, keep_default_na=False)
    df = df[~df["test_run"].astype(str).str.lower().eq("true")]
    df = df[~df["participant_id"].str.strip().isin(PILOT)]
    return df.drop_duplicates("participant_id", keep="last")      # a re-saved session counts once


def summarise(df: pd.DataFrame) -> str:
    n = len(df)
    out = [f"Peer trial: {n} participants ({', '.join(sorted(df['participant_id']))})"]
    if n == 0:
        return out[0]

    out += ["", "Task success (observed by the facilitator)",
            "| task | without help | with help | not completed | not recorded |", "|---|---|---|---|---|"]
    for col, name in TASKS.items():
        c = df[col].value_counts() if col in df else pd.Series(dtype=int)
        done = sum(c.get(k, 0) for k in ("no_help", "with_help", "failed"))
        out.append(f"| {name} | {c.get('no_help', 0)}/{n} | {c.get('with_help', 0)}/{n} | "
                   f"{c.get('failed', 0)}/{n} | {n - done}/{n} |")

    def num(col: str) -> pd.Series:
        return pd.to_numeric(df[col], errors="coerce") if col in df else pd.Series(dtype=float)

    found, removed, added = num("detected").sum(), num("removed").sum(), num("added").sum()
    out += ["", "Correction in the check step (Goal 1 in real use)"]
    if found:
        out.append(f"- tools found: {found:.0f}; removed by users (false positives): {removed:.0f} ({removed / found:.0%}); "
                   f"added by users (misses): {added:.0f} ({added / found:.0%} of found)")
        out.append(f"- participants who changed nothing: {int(((num('removed') == 0) & (num('added') == 0)).sum())}/{n}")
    shown, agreed = num("missing_shown").sum(), num("missing_agreed").sum()
    if shown:
        out.append(f"- perceived accuracy: {agreed:.0f} of {shown:.0f} missing tools agreed to be really missing "
                   f"({agreed / shown:.0%})")

    out += ["", f"Questionnaire (1 = strongly disagree, 5 = strongly agree; n = {n})",
            "| statement | median | min-max | share 4-5 |", "|---|---|---|---|"]
    for col in QUESTIONS:
        v = num(col).dropna()
        if len(v):
            out.append(f"| {col} | {v.median():g} | {v.min():g}-{v.max():g} | {(v >= 4).mean():.0%} |")

    notes = [f"- {pid}: {note}" for pid, note in zip(df["participant_id"], df.get("facilitator_notes", []))
             if str(note).strip()]
    if notes:
        out += ["", "Facilitator notes"] + notes
    return "\n".join(out)


def main() -> None:
    ap = argparse.ArgumentParser(description=__doc__, formatter_class=argparse.RawDescriptionHelpFormatter)
    ap.add_argument("sheet", type=Path, help="the study sheet exported as CSV")
    print(summarise(load(ap.parse_args().sheet)))


if __name__ == "__main__":
    main()
