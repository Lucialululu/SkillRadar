"""
Choose the embedding-linking threshold for the LLM matchers on the DEV split only, then freeze it.

    uv run python evaluation/tune_llm.py

The LLM answers are cached (data/llm_cache/), so after the first run every threshold is re-scored from
the cache: only the linking step changes, no new LLM calls. Thresholds: 0.70 ... 0.95, and 1.00 = no
embedding linking at all (alias lookup only), which is the ablation for the linking step.

Pick the threshold with the best F1 (all) under lenient scoring, write it down, then:

    export SKILLRADAR_LINK_THRESHOLD=<value>
    git tag llm-v1-frozen        # prompts, few-shot items, model and threshold are now fixed

and only then run evaluate.py on the test split. Changing anything after looking at test results makes the
comparison meaningless, exactly as with matcher-v1-frozen.
"""
from __future__ import annotations

import sys
from pathlib import Path

import pandas as pd

ROOT = Path(__file__).resolve().parents[1]
sys.path.insert(0, str(ROOT))
sys.path.insert(0, str(ROOT / "evaluation"))

import evaluate as ev  # noqa: E402
from skillradar.llm_matcher import Hybrid, LLMOnly, Settings  # noqa: E402

THRESHOLDS = [0.70, 0.75, 0.80, 0.85, 0.90, 0.95, 1.00]


def main():
    software = pd.read_csv(ev.ONET)
    norm = ev.LabelNormaliser(software)
    labels = ev.load_labels(ev.ROOT / "evaluation/labels_gold.csv", norm)
    base = Settings.from_env()
    # the few-shot example postings are inside the prompt, so scoring them would flatter the LLM
    labels = labels[(labels["split"] == "dev") & ~labels["item_id"].isin(base.fewshot)]
    texts = {i: ev.item_text(i) for i in labels["item_id"]}
    rows = []
    for cls in (LLMOnly, Hybrid):
        for th in THRESHOLDS:
            m = cls(software, settings=Settings(base.model, base.embed_model, th, base.fewshot))
            found = {r.item_id: m.extract_tools(texts[r.item_id]) for r in labels.itertuples()}
            for name, score in (("lenient", ev.score_item_lenient), ("strict", ev.score_item)):
                c = ev.total([score(found[r.item_id], r.truth) for r in labels.itertuples()])
                rows.append({"matcher": cls.__name__, "threshold": "off" if th >= 1 else th, "scoring": name,
                             "precision": ev.fmt(c.precision), "recall (all)": ev.fmt(c.recall_all),
                             "F1 (all)": ev.fmt(c.f1_all), "embedding links": m.stats["linked_embedding"],
                             "new API calls": m.stats["api_calls"]})
    df = pd.DataFrame(rows)
    print(f"dev split without the few-shot items, {len(labels)} items, model {base.model}, few-shot {base.fewshot or 'none'}\n")
    print(ev.md(df[df.scoring == "lenient"].drop(columns="scoring")))
    print("\nstrict scoring, for reference:\n")
    print(ev.md(df[df.scoring == "strict"].drop(columns="scoring")))
    best = (df[df.scoring == "lenient"].assign(f=lambda d: d["F1 (all)"].astype(float))
            .groupby("threshold")["f"].mean().sort_values(ascending=False))
    print(f"\nBest mean F1 (all) over both matchers: threshold {best.index[0]} ({best.iloc[0]:.3f}). "
          f"With 10 dev items, prefer 'off' unless a threshold is clearly better.")


if __name__ == "__main__":
    main()
