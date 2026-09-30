"""
Keyword matcher: finds O*NET tools (Python, SQL, AWS, ...) in free text.

One matcher for everything: CV text, job-posting text and the dataset's own skill
labels all go through the same vocabulary, so the numbers stay comparable.

Merged from `data_inspection_secondary.ipynb` (cell 32) and
`data_inspection_primary.ipynb` (cell 33). Differences between the two copies,
and what this module does:
  * secondary auto-dropped every alias firing in >10% of postings (could silently
    remove Excel); primary only printed them. -> here: never auto-drop.
    `suggest_drops()` prints candidates, a human puts them in MANUAL_DROP.
  * label matching lowercased the labels, so case-sensitive tools (R, Spark, Scala,
    Excel) never matched, and "scikitlearn" != "scikit-learn".
    -> `extract_tools_from_labels()` handles both.

Pipeline for building the vocabulary:
  (1) vocabulary = tools O*NET flags Hot Technology / In Demand
  (2) drop generic category entries ("Payroll software")
  (3) strip vendor names ("Microsoft Power BI" -> "Power BI")
  (4) acronyms only when they abbreviate the words before them
      ("Structured query language SQL" -> "SQL")
  (5) case-sensitive matching for names that are also English words (R, Go, Excel)
  (6) MANUAL_DROP removes aliases that turned out to be plain English

Usage:
    from skillradar.matcher import KeywordMatcher
    m = KeywordMatcher.from_csv("data/onet/software_skills.csv")
    m.extract_tools("We use Python, SQL and AWS.")   # {'Python', 'Structured query language SQL', ...}
    m.explain("... text ...")                        # {alias that fired: tool}
"""
from __future__ import annotations

import re
from collections import Counter
from pathlib import Path
from typing import Iterable

import pandas as pd

# ---------------------------------------------------------------------------
# Hand-tuned configuration. This is where almost all future fixes go.
# Every fix should also get a test case in tests/test_matcher.py.
# ---------------------------------------------------------------------------

# O*NET names we keep even though they look generic, with a nicer short alias
KEEP = {
    "Rust programming language": "Rust",
    "ANSYS simulation software": "ANSYS",
    "Shell script": "Shell scripting",
}

# single-word O*NET entries that are categories, not tools
GENERIC_SINGLE_WORDS = {
    "tax", "payroll", "productivity", "reporting", "purchasing",
    "statistical", "chatbot", "disassembler", "firewall",
}

# vendor prefixes we strip to get the name people actually write
VENDORS = [
    "Microsoft", "Apache", "Amazon", "Google", "Adobe", "Autodesk", "Atlassian",
    "Oracle", "IBM", "ESRI", "Intuit", "Apple", "The MathWorks", "MathWorks",
    "Red Hat", "Dassault Systemes", "StataCorp", "SAS",
]

# names that are too ambiguous without the vendor ("Microsoft Teams" ok, "Teams" not)
NO_SHORT = {
    "analytics", "docs", "meet", "sheets", "ads", "project", "word", "access",
    "edge", "teams", "windows", "office", "azure", "workforce now", "cloud",
    "database", "workspace", "android", "ios", "macos",
}

# tool names that are also English words: only match with exact capitalisation
CASE_SENSITIVE = {
    "C", "R", "Go", "Swift", "React", "Ruby", "Chef", "Puppet", "Slack", "Zoom",
    "Bootstrap", "Prometheus", "Snowflake", "Google", "Facebook", "Bash", "Scala",
    "Rust", "Excel", "Spark", "Hive", "Outlook", "Safari", "Unity", "REST Assured",
    "Selenium", "Postman",
}

# aliases we removed after looking at real postings (write them as they appear,
# e.g. "Go" or "google"); filled in from suggest_drops() + a human decision
MANUAL_DROP: set[str] = set()

MAX_NGRAM = 8

# keeps C++, C#, Node.js, R&D as single tokens (so "R" does not fire inside "R&D")
TOKEN = re.compile(r"[A-Za-z0-9+#&]+(?:[.-][A-Za-z0-9+#&]+)*")


# ---------------------------------------------------------------------------
# Vocabulary building (pure functions, easy to test on their own)
# ---------------------------------------------------------------------------

def tokens(text: str) -> list[str]:
    return TOKEN.findall(text)


def squash(text: str) -> str:
    """Lowercase and keep only letters, digits, + and #: 'scikit-learn' -> 'scikitlearn'."""
    return re.sub(r"[^a-z0-9+#]", "", text.lower())


def is_generic(name: str) -> bool:
    """True for category entries like 'Payroll software' or 'Data base user interface'."""
    if name in KEEP:
        return False
    words = re.sub(r"\s+(software|systems?|tools)$", "", name, flags=re.I).split()
    return (len(words) > 1 and all(w.islower() for w in words[1:])) or (
        len(words) == 1 and words[0].lower() in GENERIC_SINGLE_WORDS
    )


def is_abbrev(acr: str, words: list[str]) -> bool:
    """True if acr starts with, and contains in order, the initials of the words before it."""
    for k in range(len(words), 1, -1):
        init = "".join(w[0].upper() for w in words[-k:])
        it = iter(acr.upper())
        if init[0] == acr[0] and all(c in it for c in init):
            return True
    return False


def aliases(name: str) -> set[str]:
    """All the ways a job ad or CV might write an O*NET tool name."""
    out = {name, KEEP.get(name, name)}
    core = re.sub(r"\s+software$", "", name, flags=re.I)
    out.add(core)                                                  # "Salesforce software" -> "Salesforce"
    for v in VENDORS:                                              # "Microsoft Power BI" -> "Power BI"
        if core.startswith(v + " ") and core[len(v) + 1:].lower() not in NO_SHORT:
            out.add(core[len(v) + 1:])
    words = core.split()
    if (len(words) > 2 and re.fullmatch(r"[A-Z][A-Z0-9+#]{1,5}", words[-1])
            and is_abbrev(words[-1], words[:-1])):
        out.add(words[-1])                                         # "... language SQL" -> "SQL"
    return out


def alias_key(alias: str) -> str:
    """Lookup key: exact-case n-gram for CASE_SENSITIVE names, lowercased otherwise."""
    joined = " ".join(tokens(alias))
    return joined if alias in CASE_SENSITIVE else joined.lower()


def build_vocab(software: pd.DataFrame) -> tuple[list[str], pd.Series]:
    """Hot Technology / In Demand tools minus generic entries, plus a popularity count."""
    flags = software.groupby("Workplace Example")[["Hot Technology", "In Demand"]].agg(
        lambda s: (s == "Y").any()
    )
    important = flags.index[flags["Hot Technology"] | flags["In Demand"]]
    vocab = sorted(t for t in important if not is_generic(t))
    popularity = software["Workplace Example"].value_counts()
    return vocab, popularity


# ---------------------------------------------------------------------------
# The matcher
# ---------------------------------------------------------------------------

class KeywordMatcher:
    """Plain keyword matching against the O*NET vocabulary.

    A future TaxonomyMatcher (synonyms / embeddings) should expose the same
    `extract_tools(text) -> set[str]` so the ablation study is a one-line swap.
    """

    def __init__(self, software: pd.DataFrame, manual_drop: Iterable[str] | None = None):
        self.vocab, popularity = build_vocab(software)

        # more popular tool is assigned last, so it wins an alias two tools share
        self.alias_to_tool: dict[str, str] = {}
        for tool in sorted(self.vocab, key=lambda t: popularity.get(t, 0)):
            for a in aliases(tool):
                if tokens(a):
                    self.alias_to_tool[alias_key(a)] = tool

        self._squash_cache: dict[str, str] | None = None
        self.dropped: set[str] = set()
        for a in (MANUAL_DROP if manual_drop is None else set(manual_drop)):
            self.drop(a)

        self.max_n = min(max(len(k.split()) for k in self.alias_to_tool), MAX_NGRAM)

    @classmethod
    def from_csv(cls, path: str | Path, **kwargs) -> "KeywordMatcher":
        return cls(pd.read_csv(path), **kwargs)

    # -- editing ------------------------------------------------------------

    def drop(self, alias: str) -> None:
        """Remove an alias in whatever case it was stored ('Go', 'go' and 'GO' all work)."""
        target = " ".join(tokens(alias)).lower()
        for key in [k for k in self.alias_to_tool if k.lower() == target]:
            del self.alias_to_tool[key]
            self.dropped.add(key)
        self._squash_cache = None

    # -- matching free text ---------------------------------------------------

    def explain(self, text: str) -> dict[str, str]:
        """{alias that fired: tool it maps to}. Use this to debug a surprising match."""
        if not isinstance(text, str):
            return {}
        toks = tokens(text)
        low = [w.lower() for w in toks]
        found: dict[str, str] = {}
        for n in range(1, self.max_n + 1):
            for i in range(len(toks) - n + 1):
                for g in (" ".join(low[i:i + n]), " ".join(toks[i:i + n])):
                    if g in self.alias_to_tool:
                        found[g] = self.alias_to_tool[g]
        return found

    def extract_tools(self, text: str) -> set[str]:
        """Set of O*NET tool names mentioned in text (each tool counted once)."""
        return set(self.explain(text).values())

    # -- matching the dataset's skill labels ------------------------------------

    def extract_tools_from_labels(self, labels: Iterable[str]) -> set[str]:
        """For a skill *list* like ['python', 'r', 'scikitlearn', 'data analysis'].

        A label is a standalone skill name, so case does not carry information
        there ('r' alone means R). Each label is first looked up whole (squashed:
        lowercase, punctuation removed), and only then scanned like normal text.
        """
        index = self._squash_index()
        found = set()
        for label in labels:
            if not isinstance(label, str) or not label.strip():
                continue
            tool = index.get(squash(label))
            if tool:
                found.add(tool)
            else:
                found |= self.extract_tools(label)
        return found

    def _squash_index(self) -> dict[str, str]:
        if self._squash_cache is None:
            idx = {}
            for key, tool in self.alias_to_tool.items():
                s = squash(key)
                if s:
                    idx.setdefault(s, tool)
            self._squash_cache = idx
        return self._squash_cache

    # -- safety net ---------------------------------------------------------------

    def alias_share(self, texts: Iterable[str]) -> pd.Series:
        """Share of texts in which each alias fires, highest first."""
        texts = [t for t in texts if isinstance(t, str)]
        counts = Counter(a for t in texts for a in self.explain(t))
        return (pd.Series(counts, dtype=float) / max(len(texts), 1)).sort_values(ascending=False)

    def suggest_drops(self, texts: Iterable[str], threshold: float = 0.10) -> pd.DataFrame:
        """Aliases firing in more than `threshold` of texts. Only a suggestion:
        a real skill (Excel) can legitimately be that common. Look, decide, then
        add the English words to MANUAL_DROP."""
        share = self.alias_share(texts)
        share = share[share > threshold]
        return pd.DataFrame({
            "tool": [self.alias_to_tool[a] for a in share.index],
            "share": share.round(3).values,
        }, index=share.index)

    def __repr__(self) -> str:
        return (f"KeywordMatcher({len(self.vocab)} tools, {len(self.alias_to_tool)} aliases, "
                f"{len(self.dropped)} dropped)")
