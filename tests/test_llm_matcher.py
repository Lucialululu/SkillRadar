"""Tests for skillradar/llm_matcher.py with a fake API client: no key, no network, no data/ needed."""
import json
import sys
import zlib
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "evaluation"))

import evaluate as ev  # noqa: E402
from skillradar import llm_matcher as lm  # noqa: E402

ROWS = [
    ("Python", "Y", "Y"), ("Structured query language SQL", "Y", "Y"), ("Go", "Y", "N"),
    ("Microsoft Azure software", "Y", "Y"), ("Microsoft Power BI", "Y", "N"), ("Tableau", "Y", "N"),
]
TEXT = "You will use Python and SQL on Databricks, with dashboards in Power BI. Go further with us!"


@pytest.fixture
def software():
    return pd.DataFrame(ROWS, columns=["Workplace Example", "Hot Technology", "In Demand"])


class FakeClient:
    """Answers like a well-behaved LLM, plus one invented tool whose quote is not in the text."""

    def __init__(self):
        self.generate_calls = 0

    def generate(self, system, turns, schema):
        self.generate_calls += 1
        if schema is lm.Extraction:
            ans = {"tools": [{"name": "Python", "quote": "use Python and SQL"},
                             {"name": "SQL", "quote": "python  and SQL on"},          # case + spacing differ
                             {"name": "Databricks", "quote": "on Databricks, with"},
                             {"name": "Microsoft Power BI", "quote": "dashboards in Power BI"},
                             {"name": "Spark", "quote": "big data in Spark"}]}         # not in the text
        else:
            ans = {"verified": [{"candidate": "Python", "keep": True, "quote": "use Python"},
                                {"candidate": "SQL", "keep": True, "quote": "and SQL on"},
                                {"candidate": "Power BI", "keep": True, "quote": "in Power BI"},
                                {"candidate": "Go", "keep": False, "quote": "Go further with us"}],
                   "additional": [{"name": "Databricks", "quote": "SQL on Databricks"}]}
        return json.dumps(ans), {"input_tokens": 100, "output_tokens": 20}

    def embed(self, texts):
        """Names about Azure share one direction; every other text gets its own (no false links)."""
        def vec(t):
            v = np.zeros(64)
            v[0 if "azure" in t.lower() else 1 + zlib.crc32(t.lower().encode()) % 63] = 1.0
            return v
        return np.array([vec(t) for t in texts])


def make(cls, software, tmp_path, threshold=0.8, client=None):
    s = lm.Settings(model="fake", embed_model="fake", link_threshold=threshold, fewshot=[])
    return cls(software, client=client or FakeClient(), settings=s, cache_dir=tmp_path)


def test_grounding_check():
    assert lm.grounded("use  PYTHON and", TEXT)
    assert lm.grounded("…dashboards in Power BI…", TEXT)
    assert lm.grounded("Go further with us!", TEXT)
    assert not lm.grounded("big data in Spark", TEXT)


def test_llm_only_drops_invented_quotes_links_aliases_and_keeps_new_tools(software, tmp_path):
    m = make(lm.LLMOnly, software, tmp_path)
    found = m.extract_tools(TEXT)
    assert found == {"Python", "Structured query language SQL", "Microsoft Power BI", "OOV:Databricks"}
    assert m.stats["dropped_ungrounded"] == 1 and m.stats["kept_oov"] == 1


def test_hybrid_rejects_go_further_and_adds_missed_tools(software, tmp_path):
    client = FakeClient()
    hy = make(lm.Hybrid, software, tmp_path, client=client)
    assert hy.keyword.extract_tools(TEXT) >= {"Go"}                    # the keyword false positive
    assert hy.extract_tools(TEXT) == {"Python", "Structured query language SQL", "Microsoft Power BI", "OOV:Databricks"}
    assert hy.stats["rejected_candidates"] == 1
    verify = make(lm.HybridVerify, software, tmp_path, client=client)
    assert verify.extract_tools(TEXT) == {"Python", "Structured query language SQL", "Microsoft Power BI"}
    assert client.generate_calls == 1 and verify.stats["cached"] == 1  # same answer, served from the cache


def test_linker_uses_the_same_lookup_as_the_labels(software):
    norm, link = ev.LabelNormaliser(software), lm.Linker(software)
    for name in ["SQL", "power bi", "Python", "Go", "Structured query language SQL", "Databricks", "Azure"]:
        mapped = norm(name)
        assert (link.lookup(name) or ev.OOV + name) == mapped


def test_embedding_linking_respects_the_threshold(software):
    fake = FakeClient()
    on = lm.Linker(software, embed=fake.embed, threshold=0.8)
    assert on.link("Azure cloud") == ("Microsoft Azure software", "embedding")
    off = lm.Linker(software, embed=fake.embed, threshold=1.0)
    assert off.link("Azure cloud") == ("OOV:Azure cloud", "oov")


def test_few_shot_examples_must_come_from_dev(software, tmp_path):
    m = make(lm.LLMOnly, software, tmp_path)
    m.s.fewshot = ["post_011"]                                         # a test item
    with pytest.raises(ValueError, match="dev item"):
        m.examples()


def test_example_answers_quote_the_text(software, tmp_path):
    m = make(lm.Hybrid, software, tmp_path)
    ans = json.loads(m._example_answer(TEXT, ["Python", "SQL", "Databricks"]))
    assert {v["candidate"]: v["keep"] for v in ans["verified"]}["Go"] is False
    assert [a["name"] for a in ans["additional"]] == ["Databricks"]
    assert all(lm.grounded(a["quote"], TEXT) for a in ans["additional"])


def test_lenient_scoring_only_relaxes_out_of_vocabulary_names(software):
    assert ev.same_tool("OOV:Amazon SageMaker", "OOV:SageMaker")
    assert ev.same_tool("Microsoft Azure software", "OOV:Azure")
    assert not ev.same_tool("Go", "OOV:Golang") and not ev.same_tool("OOV:R", "OOV:Rasa")
    assert not ev.same_tool("Python", "Structured query language SQL")
    truth = {"Python", "OOV:SageMaker", "OOV:Databricks"}
    c = ev.score_item_lenient({"Python", "OOV:Amazon SageMaker", "OOV:Dask"}, truth)
    assert (c.tp, c.tp_oov, c.fp, c.fn_vocab, c.fn_oov) == (2, 1, 1, 0, 1)
    strict = ev.score_item({"Python"}, truth)                          # strict scoring is unchanged
    assert (strict.tp, strict.fp, strict.fn_vocab, strict.fn_oov) == (1, 0, 0, 2)


def test_dotenv_is_read_but_the_terminal_wins(tmp_path, monkeypatch):
    env = tmp_path / ".env"
    env.write_text('# my key\nGEMINI_API_KEY="abc123"\nexport SKILLRADAR_LLM_MODEL=from-file\n')
    monkeypatch.delenv("GEMINI_API_KEY", raising=False)
    monkeypatch.setenv("SKILLRADAR_LLM_MODEL", "from-terminal")
    lm.load_dotenv(env)
    assert lm.os.environ["GEMINI_API_KEY"] == "abc123"
    assert lm.os.environ["SKILLRADAR_LLM_MODEL"] == "from-terminal"


def test_inexact_quote_is_kept_when_the_tool_name_is_in_the_text(software, tmp_path):
    class Paraphraser(FakeClient):
        def generate(self, system, turns, schema):
            return json.dumps({"tools": [{"name": "Databricks", "quote": "runs Databricks notebooks"},   # paraphrased
                                         {"name": "Spark", "quote": "Spark clusters"}]}), {}             # invented
    m = make(lm.LLMOnly, software, tmp_path, client=Paraphraser())
    assert m.extract_tools(TEXT) == {"OOV:Databricks"}
    assert m.stats["grounded_by_name"] == 1 and m.stats["dropped_ungrounded"] == 1
