"""
Draw the evaluation postings (Goal 1) and write them out for BLIND labelling.

    uv run python evaluation/sample_postings.py                # 40 data-scientist postings, 10 dev / 30 test
    uv run python evaluation/sample_postings.py --n 40 --dev 10 --role "data scientist" --seed 42

Writes
    evaluation/items/post_001.txt ...     posting text only (gitignored: not ours to redistribute)
    evaluation/manifest.csv               item_id, split, posting_id, title (committed)
    evaluation/labels_TEMPLATE.csv        empty label sheet; each labeller copies it to labels_<name>.csv

Nothing here shows what the matcher finds. Label first, run evaluate.py afterwards.
Run it ONCE and commit manifest.csv, so the sample cannot drift.
"""
from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from skillradar.demand import PROCESSED, SOURCES

HERE = Path(__file__).resolve().parent


def draw(pt: pd.DataFrame, role: str, n: int, dev: int, seed: int) -> pd.DataFrame:
    """Random sample of one role's postings, first `dev` rows are the dev split."""
    pool = pt[pt["role"] == role]
    if len(pool) < n:
        raise ValueError(f"only {len(pool)} postings for {role}")
    s = pool.sample(n, random_state=seed).reset_index(drop=True)
    return pd.DataFrame({
        "item_id": [f"post_{i + 1:03d}" for i in range(n)],
        "split": ["dev" if i < dev else "test" for i in range(n)],
        "posting_id": s["posting_id"],
        "title": s["title"],
    })


def fetch_texts(ids: set, source: str) -> dict:
    if source == "primary":
        out = {}
        for chunk in pd.read_csv(SOURCES["primary"] / "job_summary.csv", chunksize=100_000):
            hit = chunk[chunk["job_link"].isin(ids)]
            out.update(zip(hit["job_link"], hit["job_summary"]))
            if len(out) >= len(ids):
                break
        return out
    p = pd.read_csv(SOURCES["secondary"] / "postings.csv", usecols=["job_id", "description", "skills_desc"])
    p = p[p["job_id"].isin(ids)]
    return dict(zip(p["job_id"], p["description"].fillna("") + "\n" + p["skills_desc"].fillna("")))


def write_items(manifest: pd.DataFrame, texts: dict, out: Path) -> None:
    (out / "items").mkdir(parents=True, exist_ok=True)
    for _, r in manifest.iterrows():
        body = texts.get(r["posting_id"])
        if not isinstance(body, str):
            raise ValueError(f"no text for {r['posting_id']}")
        (out / "items" / f"{r['item_id']}.txt").write_text(f"TITLE: {r['title']}\n\n{body}\n", encoding="utf-8")
    manifest.to_csv(out / "manifest.csv", index=False)
    template = manifest[["item_id", "split"]].assign(labeller="", true_tools="", notes="")
    template.to_csv(out / "labels_TEMPLATE.csv", index=False)


def main(argv=None):
    ap = argparse.ArgumentParser(description="sample postings for blind labelling")
    ap.add_argument("--role", default="data scientist")
    ap.add_argument("--source", choices=["primary", "secondary"], default="primary")
    ap.add_argument("--n", type=int, default=40)
    ap.add_argument("--dev", type=int, default=10)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--force", action="store_true", help="overwrite an existing manifest.csv")
    args = ap.parse_args(argv)

    if (HERE / "manifest.csv").exists() and not args.force:
        raise SystemExit("evaluation/manifest.csv exists already. The sample is fixed; use --force only "
                         "if you really want a new one (and throw away labels made on the old one).")
    pt = pd.read_csv(PROCESSED / f"posting_tools_{args.source}.csv", keep_default_na=False)
    manifest = draw(pt, args.role, args.n, args.dev, args.seed)
    texts = fetch_texts(set(manifest["posting_id"]), args.source)
    write_items(manifest, texts, HERE)
    print(f"wrote {len(manifest)} postings to evaluation/items/ "
          f"({(manifest['split'] == 'dev').sum()} dev / {(manifest['split'] == 'test').sum()} test)")
    print("next: copy labels_TEMPLATE.csv to labels_<yourname>.csv and label, see evaluation/GUIDELINES.md")


if __name__ == "__main__":
    main()
