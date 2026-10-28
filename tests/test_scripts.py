"""Tests for the helper scripts in scripts/ (no data/ folder needed)."""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).resolve().parents[1] / "scripts"))

from alias_snippets import find_snippets  # noqa: E402


def test_snippets_respect_tokens_and_case():
    text = "We use C++ and C# daily. Knowledge of C is a plus. Go further with Go-to tools. We write Go."
    c = find_snippets(text, "C", case_sensitive=True)
    assert len(c) == 1 and "[[C]] is a plus" in c[0]
    go = find_snippets(text, "Go", case_sensitive=True)
    assert len(go) == 2                               # "Go further" and "write Go." but not "Go-to"
    assert find_snippets("go to market", "Go", case_sensitive=True) == []


def test_snippets_skip_glued_tokens():
    assert find_snippets("Experience with Objective-C required", "C", case_sensitive=True) == []
    assert find_snippets(None, "C", True) == []
