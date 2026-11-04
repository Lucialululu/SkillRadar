"""
LLM-based tool extraction: the Goal 1 method comparison (keyword vs LLM vs hybrid).

Three matchers. Each exposes extract_tools(text) -> set[str] and is built as Class(software_df),
so evaluation/evaluate.py can swap them in with --matcher:

    LLMOnly         the LLM reads the text and lists every named tool (open vocabulary)
    Hybrid          the frozen keyword matcher proposes candidates; the LLM keeps or rejects each one
                    in context, and adds tools the keywords missed  (after Clavié & Soulié 2023)
    HybridVerify    the same LLM answer as Hybrid, but only the keep/reject part is used (no additions).
                    Separates "context checking" from "better coverage" at no extra API cost.

Pipeline for one text:

    text ──► prompt (rules = our labelling guidelines, few-shot examples from the DEV split,
             JSON schema, temperature 0) ──► LLM answer: tool name + quote per tool
         ──► grounding check: a tool is kept only if its quote occurs in the text, or else its name does
             (hallucination guard; tools whose quote and name are both missing are dropped and counted)
         ──► linking: name -> O*NET vocabulary tool
               1. the same alias lookup used for the human labels (evaluate.LabelNormaliser)
               2. otherwise the nearest vocabulary tool by embedding similarity, if cosine >= threshold
               3. otherwise kept as an out-of-vocabulary tool "OOV:<name>"

Nothing here is trained. Two settings are chosen on the dev split and then frozen before the test:
the few-shot examples and the linking threshold (evaluation/tune_llm.py).

Every LLM and embedding answer is cached in data/llm_cache/ (gitignored: answers on CVs contain CV
quotes), so re-scoring, tuning the threshold or rerunning evaluate.py costs no further API calls,
and the raw answers can be inspected.

Setup (key from aistudio.google.com; .env is gitignored, never commit the key):
    echo 'GEMINI_API_KEY=...' > .env                # or: export GEMINI_API_KEY=... in the terminal
    uv run python -m skillradar.llm_matcher --try "We use Python, Databricks and Power BI."
    uv run python -m skillradar.llm_matcher --list-models

Settings (environment variables, read when a matcher is built):
    SKILLRADAR_LLM_MODEL        default gemini-3.8-flash
    SKILLRADAR_EMBED_MODEL      default gemini-embedding-001
    SKILLRADAR_LINK_THRESHOLD   default 0.80   (1.0 switches embedding linking off)
    SKILLRADAR_FEWSHOT          default post_003,post_005   (dev items only; "" = zero-shot)

Privacy: posting texts are public. Do not send CVs on the free API tier (Google may use free-tier
inputs to improve its products); enable billing on the key first, and only with the person's consent.
"""
from __future__ import annotations

import argparse
import hashlib
import json
import os
import re
import sys
import time
from dataclasses import dataclass, field
from pathlib import Path
from typing import Callable, Iterable

import numpy as np
import pandas as pd
from pydantic import BaseModel

from skillradar.matcher import KeywordMatcher, aliases, squash
from skillradar.report import display_name

ROOT = Path(__file__).resolve().parents[1]
CACHE = ROOT / "data" / "llm_cache"
ITEMS = ROOT / "evaluation" / "items"
GOLD = ROOT / "evaluation" / "labels_gold.csv"
OOV = "OOV:"
PROMPT_VERSION = "v1"            # bump when a prompt changes, so old cached answers are not reused
MAX_EXAMPLE_CHARS = 4000         # few-shot example texts are cut to this length
MAX_QUOTE_WORDS = 12


# ---------------------------------------------------------------------------
# settings
# ---------------------------------------------------------------------------

def load_dotenv(path: Path = ROOT / ".env") -> None:
    """Read KEY=value lines from the repo's .env file (gitignored) into the environment.
    Variables already set in the terminal win. Lines starting with # are skipped."""
    if not path.exists():
        return
    for line in path.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        key, value = line.split("=", 1)
        key = key.removeprefix("export ").strip()
        os.environ.setdefault(key, value.strip().strip('"').strip("'"))


@dataclass
class Settings:
    model: str = "gemini-3.8-flash"
    embed_model: str = "gemini-embedding-001"
    link_threshold: float = 0.80
    fewshot: list[str] = field(default_factory=lambda: ["post_003", "post_005"])

    @classmethod
    def from_env(cls) -> "Settings":
        load_dotenv()
        d = cls()
        fs = os.environ.get("SKILLRADAR_FEWSHOT")
        return cls(
            model=os.environ.get("SKILLRADAR_LLM_MODEL", d.model),
            embed_model=os.environ.get("SKILLRADAR_EMBED_MODEL", d.embed_model),
            link_threshold=float(os.environ.get("SKILLRADAR_LINK_THRESHOLD", d.link_threshold)),
            fewshot=d.fewshot if fs is None else [s.strip() for s in fs.split(",") if s.strip()],
        )


# ---------------------------------------------------------------------------
# answer formats (sent to the API as JSON schemas)
# ---------------------------------------------------------------------------

class Tool(BaseModel):
    name: str
    quote: str


class Extraction(BaseModel):
    tools: list[Tool]


class Verdict(BaseModel):
    candidate: str
    keep: bool
    quote: str


class Verification(BaseModel):
    verified: list[Verdict]
    additional: list[Tool]


RULES = """A tool is a named product, programming language, library, framework, database, cloud service or platform
that the text says is used, required, wanted or part of the work. Examples: Python, SQL, AWS, Tableau, scikit-learn,
Databricks, Excel, Git.
Not tools: company names used as employers ("Google is an equal opportunity employer"), ordinary English words
("Go further", "excel at communication", "C-level"), general skills or methods ("machine learning", "statistics",
"A/B testing", "data visualization"), job titles, degrees.
Name each tool once, the way people normally write it ("Power BI", not "Microsoft Power BI software").
For every tool copy a short quote from the text, at most 12 words, character for character, that shows it.
Only list tools that appear in the text. Never add tools that are merely typical for the role."""

SYSTEM_EXTRACT = ("You extract named software tools and technologies from a job posting or a CV.\n" + RULES +
                  "\nAnswer with JSON matching the schema: {\"tools\": [{\"name\": ..., \"quote\": ...}]}.")

SYSTEM_VERIFY = ("You check and complete a list of software tools found in a job posting or a CV.\n" + RULES + """
After the text you get CANDIDATES that a keyword matcher found, each with the words it matched.
1. For every candidate decide whether the text really refers to that tool: keep=true, with a quote.
   keep=false if the words mean something else here (a company, an English word, another product), with the quote
   that shows this.
2. In "additional", list every other tool in the text that the candidates missed, with a quote.
Answer with JSON matching the schema: {"verified": [{"candidate", "keep", "quote"}], "additional": [{"name", "quote"}]}.""")


# ---------------------------------------------------------------------------
# small text helpers
# ---------------------------------------------------------------------------

_PUNCT = str.maketrans({"’": "'", "‘": "'", "“": '"', "”": '"', "–": "-", "—": "-", " ": " "})


def _norm(s: str) -> str:
    return " ".join(s.translate(_PUNCT).lower().split())


def grounded(quote: str, text: str) -> bool:
    """True if the quote really occurs in the text (ignoring case, spacing, curly quotes and a leading or
    trailing ellipsis). This is the hallucination guard: a tool whose evidence is invented is dropped."""
    q = _norm(quote).strip(" .…\"'")
    while q.startswith("..."):
        q = q[3:].strip()
    while q.endswith("..."):
        q = q[:-3].strip()
    return len(q) >= 1 and q in _norm(text)


def find_quote(names: Iterable[str], text: str, words: int = 5) -> str | None:
    """A short, exact quote around the first place where any of `names` occurs as whole words."""
    for name in sorted({n for n in names if n}, key=len, reverse=True):
        m = re.search(r"(?<![A-Za-z0-9])" + re.escape(name) + r"(?![A-Za-z0-9])", text, flags=re.I)
        if not m:
            continue
        spans = [w.span() for w in re.finditer(r"\S+", text)]
        i = next(k for k, (s, e) in enumerate(spans) if e > m.start())
        j = next((k for k, (s, e) in enumerate(spans) if e >= m.end()), i)
        lo, hi = spans[max(0, i - words)][0], spans[min(len(spans) - 1, j + words)][1]
        return text[lo:hi]
    return None


def _strip_marks(snippet: str) -> str:
    """matcher.evidence() snippet -> plain quote of at most MAX_QUOTE_WORDS words around the match."""
    s = snippet.strip("…")
    m = re.search(r"\*\*(.+?)\*\*", s)
    if not m:
        return s.replace("**", "")
    before = s[:m.start()].split()[-4:]
    after = s[m.end():].split()[:4]
    return " ".join(before + [m.group(1)] + after).replace("**", "")


# ---------------------------------------------------------------------------
# the API client (thin, so tests can pass a fake one)
# ---------------------------------------------------------------------------

class GeminiClient:
    """generate(system, turns, schema) -> (json text, usage) and embed(texts) -> array, with retries."""

    def __init__(self, model: str, embed_model: str):
        load_dotenv()
        key = os.environ.get("GEMINI_API_KEY") or os.environ.get("GOOGLE_API_KEY")
        if not key:
            raise RuntimeError("No API key. Put GEMINI_API_KEY=... in the repo's .env file, "
                               "or run: export GEMINI_API_KEY=...  (key from aistudio.google.com)")
        from google import genai                      # imported here so the app never needs it
        from google.genai import types
        self.types = types
        # one request may take at most 120 s; slow "thinking" answers then fail visibly instead of hanging
        self.client = genai.Client(api_key=key, http_options=types.HttpOptions(timeout=120_000))
        self.model, self.embed_model = model, embed_model

    def _retry(self, fn, what: str):
        for attempt in range(6):
            t0 = time.time()
            print(f"[llm_matcher] {what} ...", file=sys.stderr, flush=True)
            try:
                out = fn()
                print(f"[llm_matcher] answer after {time.time() - t0:.1f}s", file=sys.stderr, flush=True)
                return out
            except Exception as err:                  # rate limit / overloaded: wait and try again
                msg = f"{type(err).__name__}: {err}"
                temporary = ("429", "RESOURCE_EXHAUSTED", "503", "500", "UNAVAILABLE", "Timeout", "timed out")
                if attempt == 5 or not any(c in msg for c in temporary):
                    raise
                # a quota error (429) is a per-minute limit: wait out the minute; overload (5xx): back off
                wait = 65 if ("429" in msg or "RESOURCE_EXHAUSTED" in msg) else min(60, 4 * 2 ** attempt)
                print(f"[llm_matcher] {msg[:160]}\n[llm_matcher] waiting {wait}s, then retry {attempt + 1} of 5",
                      file=sys.stderr, flush=True)
                time.sleep(wait)

    def generate(self, system: str, turns: list[tuple[str, str]], schema: type[BaseModel]) -> tuple[str, dict]:
        t = self.types
        contents = [t.Content(role=role, parts=[t.Part(text=txt)]) for role, txt in turns]
        config = t.GenerateContentConfig(system_instruction=system, temperature=0,
                                         response_mime_type="application/json", response_schema=schema)
        r = self._retry(lambda: self.client.models.generate_content(model=self.model, contents=contents, config=config),
                        f"asking {self.model}")
        u = r.usage_metadata
        usage = {"input_tokens": getattr(u, "prompt_token_count", 0) or 0,
                 "output_tokens": (getattr(u, "candidates_token_count", 0) or 0) + (getattr(u, "thoughts_token_count", 0) or 0)}
        return r.text, usage

    def embed(self, texts: list[str]) -> np.ndarray:
        cfg = self.types.EmbedContentConfig(task_type="SEMANTIC_SIMILARITY", output_dimensionality=768)
        out = []
        for i in range(0, len(texts), 100):
            r = self._retry(lambda: self.client.models.embed_content(
                model=self.embed_model, contents=texts[i:i + 100], config=cfg),
                f"embedding {len(texts[i:i + 100])} names with {self.embed_model}")
            out += [e.values for e in r.embeddings]
        return np.asarray(out, dtype=float)


# ---------------------------------------------------------------------------
# linking names onto the O*NET vocabulary
# ---------------------------------------------------------------------------

class Linker:
    """Maps a tool name onto our O*NET vocabulary.

    Step 1 is deliberately the SAME lookup that evaluate.LabelNormaliser applies to the human labels, so the
    labels and the LLM's names are normalised identically. Step 2 (embeddings) only runs for names that
    step 1 cannot place; step 3 keeps the rest as out-of-vocabulary tools."""

    def __init__(self, software: pd.DataFrame, embed: Callable[[list[str]], np.ndarray] | None = None,
                 threshold: float = 0.80):
        self.m = KeywordMatcher(software, manual_drop=[])
        self.vocab = sorted(self.m.vocab)
        self.index = dict(self.m._squash_index())
        for tool in self.vocab:
            self.index.setdefault(squash(tool), tool)
            self.index.setdefault(squash(display_name(tool)), tool)
        self.embed, self.threshold = embed, threshold
        self._vocab_emb: np.ndarray | None = None

    def lookup(self, name: str) -> str | None:
        name = name.strip()
        tool = self.index.get(squash(name))
        if tool:
            return tool
        found = self.m.extract_tools(name)
        return found.pop() if len(found) == 1 else None

    def vocab_texts(self) -> list[str]:
        return [display_name(t) if display_name(t) == t else f"{display_name(t)} ({t})" for t in self.vocab]

    def nearest(self, name: str) -> tuple[str, float]:
        if self._vocab_emb is None:
            self._vocab_emb = _unit(self.embed(self.vocab_texts()))
        sims = self._vocab_emb @ _unit(self.embed([name.strip()]))[0]
        k = int(np.argmax(sims))
        return self.vocab[k], float(sims[k])

    def link(self, name: str) -> tuple[str, str]:
        """-> (vocabulary tool or 'OOV:<name>', how: 'alias' | 'embedding' | 'oov')"""
        tool = self.lookup(name)
        if tool:
            return tool, "alias"
        if self.embed is not None and self.threshold < 1.0 and name.strip():
            tool, sim = self.nearest(name)
            if sim >= self.threshold:
                return tool, "embedding"
        return OOV + name.strip(), "oov"


def _unit(x: np.ndarray) -> np.ndarray:
    return x / np.clip(np.linalg.norm(x, axis=-1, keepdims=True), 1e-12, None)


# ---------------------------------------------------------------------------
# the matchers
# ---------------------------------------------------------------------------

class _LLMMatcher:
    task = "extract"                     # or "verify"

    def __init__(self, software: pd.DataFrame, client=None, settings: Settings | None = None,
                 cache_dir: Path | None = CACHE):
        self.s = settings or Settings.from_env()
        self._client = client
        self.cache_dir = cache_dir
        self.keyword = KeywordMatcher(software)               # the frozen keyword rules (matcher-v1-frozen)
        self.linker = Linker(software, embed=self._embed, threshold=self.s.link_threshold)
        self.stats = {"texts": 0, "api_calls": 0, "cached": 0, "input_tokens": 0, "output_tokens": 0,
                      "seconds": 0.0, "dropped_ungrounded": 0, "grounded_by_name": 0, "rejected_candidates": 0,
                      "linked_alias": 0, "linked_embedding": 0, "kept_oov": 0}
        self.details: dict[str, dict] = {}                   # per text, for error analysis
        self._examples = None

    # -- infrastructure -----------------------------------------------------------------

    @property
    def client(self):
        if self._client is None:
            self._client = GeminiClient(self.s.model, self.s.embed_model)
        return self._client

    def _cached(self, kind: str, key_obj, compute):
        key = hashlib.sha256(json.dumps(key_obj, sort_keys=True).encode()).hexdigest()[:24]
        path = self.cache_dir / kind / f"{key}.json" if self.cache_dir else None
        if path and path.exists():
            return json.loads(path.read_text()), True
        value = compute()
        if path:
            path.parent.mkdir(parents=True, exist_ok=True)
            path.write_text(json.dumps(value))
        return value, False

    def _embed(self, texts: list[str]) -> np.ndarray:
        value, _ = self._cached("embed", {"model": self.s.embed_model, "texts": texts},
                                lambda: self.client.embed(texts).round(6).tolist())
        return np.asarray(value, dtype=float)

    def _ask(self, system: str, turns: list[tuple[str, str]], schema: type[BaseModel]) -> BaseModel:
        def call():
            t0 = time.time()
            text, usage = self.client.generate(system, turns, schema)
            return {"text": text, "usage": usage, "seconds": round(time.time() - t0, 3)}
        key = {"model": self.s.model, "prompt": PROMPT_VERSION, "system": system, "turns": turns, "schema": schema.__name__}
        value, hit = self._cached("generate", key, call)
        self.stats["cached" if hit else "api_calls"] += 1
        self.stats["input_tokens"] += value["usage"].get("input_tokens", 0)
        self.stats["output_tokens"] += value["usage"].get("output_tokens", 0)
        self.stats["seconds"] += value["seconds"]
        return schema.model_validate_json(value["text"])

    # -- prompts --------------------------------------------------------------------------

    def _user_turn(self, text: str) -> str:
        msg = f"TEXT:\n<<<\n{text}\n>>>"
        if self.task == "verify":
            ev = self.keyword.evidence(text)
            cands = sorted(self.keyword.extract_tools(text), key=lambda t: display_name(t).lower())
            lines = [f'- {display_name(c)}: "{_strip_marks(ev.get(c, ""))}"' for c in cands]
            msg += "\nCANDIDATES:\n" + ("\n".join(lines) if lines else "(none)")
        return msg

    def examples(self) -> list[tuple[str, str]]:
        """Few-shot turns built from DEV items and their gold labels (never test items)."""
        if self._examples is not None:
            return self._examples
        turns: list[tuple[str, str]] = []
        if self.s.fewshot:
            gold = pd.read_csv(GOLD, dtype=str, keep_default_na=False).set_index("item_id")
            for item in self.s.fewshot:
                if item not in gold.index or gold.loc[item, "split"] != "dev":
                    raise ValueError(f"few-shot example {item!r} is not a labelled dev item; test items must stay unseen")
                path = ITEMS / f"{item}.txt"
                if not path.exists():
                    print(f"[llm_matcher] {path} missing, running zero-shot", file=sys.stderr)
                    turns = []
                    break
                text = path.read_text(encoding="utf-8")[:MAX_EXAMPLE_CHARS]
                names = [t.strip() for t in gold.loc[item, "true_tools"].replace(",", ";").split(";") if t.strip()]
                turns += [("user", self._user_turn(text)), ("model", self._example_answer(text, names))]
        self._examples = turns
        return turns

    def _example_answer(self, text: str, names: list[str]) -> str:
        def quote_for(name):
            tool = self.linker.lookup(name)
            return find_quote([name] + (sorted(aliases(tool)) + [display_name(tool)] if tool else []), text)
        if self.task == "extract":
            tools = [{"name": n, "quote": q} for n in names if (q := quote_for(n))]
            return json.dumps({"tools": tools})
        gold_tools = {self.linker.lookup(n) or n for n in names}
        ev = self.keyword.evidence(text)
        cands = sorted(self.keyword.extract_tools(text), key=lambda t: display_name(t).lower())
        verified = [{"candidate": display_name(c), "keep": c in gold_tools, "quote": _strip_marks(ev.get(c, ""))}
                    for c in cands]
        additional = [{"name": n, "quote": q} for n in names
                      if (self.linker.lookup(n) or n) not in set(cands) and (q := quote_for(n))]
        return json.dumps({"verified": verified, "additional": additional})

    # -- the interface evaluate.py uses ----------------------------------------------------

    def _link_all(self, tools: list[Tool], text: str, info: dict) -> set[str]:
        out = set()
        for t in tools:
            if not grounded(t.quote, text):
                # the LLM often names a real tool but does not copy its quote exactly: keep the tool if its
                # name itself occurs in the text as whole words; drop it only if the name is not there either
                if find_quote([t.name], text, words=0) is None:
                    self.stats["dropped_ungrounded"] += 1
                    info["dropped"].append(t.name)
                    continue
                self.stats["grounded_by_name"] += 1
            tool, how = self.linker.link(t.name)
            self.stats[{"alias": "linked_alias", "embedding": "linked_embedding", "oov": "kept_oov"}[how]] += 1
            if how == "embedding":
                info["embedding_links"].append(f"{t.name} -> {display_name(tool)}")
            out.add(tool)
        return out

    def extract_tools(self, text: str) -> set[str]:
        raise NotImplementedError


class LLMOnly(_LLMMatcher):
    """Open-vocabulary extraction by the LLM alone, then grounding check and linking."""
    task = "extract"

    def extract_tools(self, text: str) -> set[str]:
        self.stats["texts"] += 1
        answer = self._ask(SYSTEM_EXTRACT, self.examples() + [("user", self._user_turn(text))], Extraction)
        info = {"dropped": [], "embedding_links": []}
        found = self._link_all(answer.tools, text, info)
        self.details[hashlib.sha1(text.encode()).hexdigest()[:10]] = info
        return found


class Hybrid(_LLMMatcher):
    """Keyword candidates, verified in context by the LLM, plus the LLM's additions."""
    task = "verify"
    add = True

    def extract_tools(self, text: str) -> set[str]:
        self.stats["texts"] += 1
        cands = self.keyword.extract_tools(text)
        answer = self._ask(SYSTEM_VERIFY, self.examples() + [("user", self._user_turn(text))], Verification)
        by_name = {squash(v.candidate): v for v in answer.verified}
        kept = set()
        for c in cands:
            v = by_name.get(squash(display_name(c))) or by_name.get(squash(c))
            if v is not None and not v.keep:
                self.stats["rejected_candidates"] += 1
            else:                                   # kept, or not answered: trust the keyword match
                kept.add(c)
        info = {"dropped": [], "embedding_links": [], "rejected": sorted(display_name(c) for c in cands - kept)}
        if self.add:
            kept |= self._link_all(answer.additional, text, info)
        self.details[hashlib.sha1(text.encode()).hexdigest()[:10]] = info
        return kept


class HybridVerify(Hybrid):
    """Ablation of Hybrid: only the keep/reject decisions, no additions (same cached LLM answer)."""
    add = False


# ---------------------------------------------------------------------------
# command line: quick checks before running the evaluation
# ---------------------------------------------------------------------------

def main(argv=None):
    ap = argparse.ArgumentParser(description="LLM matcher: quick checks (see module docstring)")
    ap.add_argument("--try", dest="text", help="run LLMOnly and Hybrid on this text and print the result")
    ap.add_argument("--list-models", action="store_true", help="list the Gemini models this key can use")
    args = ap.parse_args(argv)
    s = Settings.from_env()
    if args.list_models:
        c = GeminiClient(s.model, s.embed_model)
        rows = []
        for m in c.client.models.list():
            acts = set(getattr(m, "supported_actions", None) or [])
            use = ("chat: SKILLRADAR_LLM_MODEL" if "generateContent" in acts else
                   "embeddings: SKILLRADAR_EMBED_MODEL" if "embedContent" in acts else None)
            if use:
                rows.append((use, m.name.removeprefix("models/")))
        for use, name in sorted(rows):
            print(f"{name:45s} {use}")
        print("\nPut the exact name in .env. Prefer a 'flash' or 'flash-lite' chat model; "
              "previews and 'pro' models often have little or no free quota.")
        return
    if args.text:
        software = pd.read_csv(ROOT / "data/onet/software_skills.csv")
        for cls in (LLMOnly, Hybrid):
            m = cls(software, settings=Settings(s.model, s.embed_model, s.link_threshold, fewshot=[]))
            tools = m.extract_tools(args.text)
            print(f"{cls.__name__:8s} {sorted(display_name(t) if not t.startswith(OOV) else t for t in tools)}")
            print(f"         {m.stats}")
        return
    ap.print_help()


if __name__ == "__main__":
    main()
