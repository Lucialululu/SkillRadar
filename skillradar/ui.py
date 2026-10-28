"""
Look and feel of the web app (app.py), following the Figma design:
near-black base with a teal (#18D9B5) glow, glass cards, Geist type.

Everything here only builds HTML/CSS strings. No app logic lives here, so
app.py stays readable and these helpers can be unit-tested (tests/test_ui.py).

Every piece of user or CV text is passed through html.escape before it goes
into the page, so a CV containing "<script>" is shown as text, never run.
"""
from __future__ import annotations

import html
import re

TEAL = "#18D9B5"

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Geist:wght@400;500;600&display=swap');

:root {
  --teal: #18D9B5; --teal-soft: rgba(24,217,181,.10); --teal-line: rgba(24,217,181,.35);
  --bg: #04080A; --text: #F2F7F6; --text2: #A3B3B0; --text3: #667673;
  --glass: rgba(255,255,255,.045); --glass2: rgba(255,255,255,.08);
  --line: rgba(255,255,255,.10); --line2: rgba(255,255,255,.16);
}
/* set on the root only: icons keep their own icon font */
html, body, .stApp {
  font-family: 'Geist', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif;
}
.stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button p, .stMarkdown { font-family: inherit; }
.stApp {
  background:
    radial-gradient(ellipse 60% 45% at 50% -8%, rgba(24,217,181,.20), transparent 70%),
    radial-gradient(ellipse 70% 40% at 50% 112%, rgba(11,94,80,.45), transparent 70%),
    var(--bg);
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
.block-container { max-width: 1120px; padding-top: 2rem; }

/* headings */
.sr-eyebrow { color: var(--teal); font-size: 12px; font-weight: 600; letter-spacing: .12em; text-transform: uppercase; margin: 8px 0 6px; }
.sr-h1 { color: var(--text); font-size: 44px; font-weight: 600; letter-spacing: -0.025em; line-height: 1.1; margin: 0 0 10px; }
.sr-hero { font-size: 54px; text-align: center; letter-spacing: -0.03em; max-width: 780px; margin: 0 auto 12px; }
.sr-sub.sr-center { max-width: 620px; margin: 0 auto 26px; }
.sr-sub { color: var(--text2); font-size: 17px; line-height: 1.55; margin: 0 0 22px; }
.sr-center { text-align: center; }
.sr-muted { color: var(--text3); font-size: 13px; }

/* top bar */
.sr-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin-bottom: 28px; flex-wrap: wrap; }
.sr-logo { display: flex; align-items: center; gap: 10px; color: var(--text); font-weight: 600; font-size: 18px; letter-spacing: -0.01em; }
.sr-steps { display: flex; gap: 4px; padding: 5px; border-radius: 999px; background: var(--glass); border: 1px solid var(--line); }
.sr-step { display: flex; align-items: center; gap: 8px; padding: 6px 14px 6px 8px; border-radius: 999px; color: var(--text3); font-size: 14px; font-weight: 500; border: 1px solid transparent; }
.sr-step .n { width: 22px; height: 22px; border-radius: 999px; display: grid; place-items: center; font-size: 12px; background: var(--glass2); border: 1px solid var(--line2); color: var(--text2); }
.sr-step.done { color: var(--text2); }
.sr-step.done .n { background: var(--teal-soft); border-color: var(--teal-line); color: var(--teal); }
.sr-step.active { color: var(--text); background: var(--teal-soft); border-color: var(--teal-line); }
.sr-step.active .n { background: var(--teal); border-color: var(--teal); color: var(--bg); }
.sr-pill { display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px; border-radius: 999px; background: var(--glass); border: 1px solid var(--line); color: var(--text2); font-size: 13px; font-weight: 500; }

/* glass card */
.sr-card { background: var(--glass); border: 1px solid var(--line); border-radius: 20px; padding: 22px 24px; backdrop-filter: blur(20px); }
.sr-card.strong { background: var(--glass2); }
.sr-card h4 { color: var(--text); font-size: 17px; font-weight: 600; margin: 0 0 8px; }
.sr-card p { color: var(--text2); font-size: 14px; line-height: 1.55; margin: 0; }

/* radar hero */
.sr-radar { position: relative; width: 260px; height: 260px; margin: 0 auto 8px; }
.sr-radar .ring { position: absolute; border-radius: 50%; border: 1px solid var(--line2); }
.sr-radar .orb { position: absolute; left: 50%; top: 50%; width: 96px; height: 96px; margin: -48px 0 0 -48px; border-radius: 50%;
  background: radial-gradient(circle at 38% 34%, #C8FFF3 0%, var(--teal) 40%, #03372E 100%); box-shadow: 0 0 60px rgba(24,217,181,.55); }
.sr-radar .sweep { position: absolute; inset: 0; border-radius: 50%;
  background: conic-gradient(from 20deg, rgba(24,217,181,.35), transparent 22%); animation: sr-spin 6s linear infinite; }
.sr-radar .blip { position: absolute; padding: 4px 10px; border-radius: 999px; font-size: 12px; color: var(--text2); background: var(--glass2); border: 1px solid var(--line); white-space: nowrap; }
.sr-radar .blip.on { color: var(--text); }
.sr-radar .blip.on::before { content: ""; display: inline-block; width: 6px; height: 6px; border-radius: 50%; background: var(--teal); margin-right: 6px; box-shadow: 0 0 8px var(--teal); }
@keyframes sr-spin { to { transform: rotate(360deg); } }

/* tool rows (step 3) */
.sr-tool { padding: 2px 0 6px; }
.sr-tool .name { color: var(--text); font-weight: 600; font-size: 16px; }
.sr-tool .ev { color: var(--text3); font-size: 13px; margin-top: 2px; }
.sr-tool .ev mark { background: none; color: var(--teal); font-weight: 500; }
.sr-tool.off .name { color: var(--text3); text-decoration: line-through; }
.sr-tool.off .ev mark { color: var(--text2); }

/* stats */
.sr-stats { display: flex; gap: 10px; margin-top: 16px; }
.sr-stat { flex: 1; padding: 10px 14px; border-radius: 14px; background: var(--glass); border: 1px solid var(--line); }
.sr-stat b { display: block; font-size: 26px; font-weight: 600; letter-spacing: -0.02em; color: var(--text); }
.sr-stat b.teal { color: var(--teal); }
.sr-stat span { color: var(--text3); font-size: 12px; }

/* gap bars (step 4) */
.sr-gap { display: grid; grid-template-columns: 24px 112px 1fr 104px 150px; align-items: center; gap: 14px; padding: 13px 18px; border-radius: 14px; background: var(--glass); margin-bottom: 8px; }
.sr-gap .rank { color: var(--text3); font-size: 13px; font-weight: 500; }
.sr-gap .tool { color: var(--text); font-weight: 600; font-size: 16px; }
.sr-gap .track { position: relative; height: 10px; border-radius: 999px; background: rgba(255,255,255,.06); }
.sr-gap .fill { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 999px; background: linear-gradient(90deg, #0B5E50, var(--teal)); box-shadow: 0 0 12px rgba(24,217,181,.45); }
.sr-gap .ci { position: absolute; top: 4px; height: 2px; background: rgba(242,247,246,.75); border-radius: 2px; }
.sr-gap .pct { color: var(--text); font-size: 18px; font-weight: 600; letter-spacing: -0.01em; }
.sr-gap .pct small { color: var(--text3); font-size: 12px; font-weight: 400; margin-left: 6px; }
.sr-gap .sr-tag { justify-self: end; }
.sr-tag { padding: 3px 10px; border-radius: 999px; font-size: 12px; font-weight: 500; background: var(--teal-soft); color: var(--teal); white-space: nowrap; }
.sr-tag.grey { background: var(--glass2); color: var(--text2); }

/* chips */
.sr-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 8px 0; }
.sr-chip { display: inline-flex; align-items: center; gap: 8px; padding: 7px 14px; border-radius: 999px; background: var(--glass); border: 1px solid var(--line); color: var(--text); font-size: 14px; font-weight: 600; }
.sr-chip::before { content: ""; width: 6px; height: 6px; border-radius: 50%; background: var(--teal); }
.sr-chip span { color: var(--text3); font-weight: 400; font-size: 13px; }
.sr-chip.added { border-color: var(--teal-line); }
.sr-chip.added span { color: var(--teal); }

/* coverage ring */
.sr-ring { position: relative; width: 190px; height: 190px; margin: 4px auto 14px; }
.sr-ring .val { position: absolute; inset: 0; display: grid; place-content: center; text-align: center; }
.sr-ring .val b { font-size: 46px; font-weight: 600; letter-spacing: -0.03em; color: var(--text); line-height: 1; }
.sr-ring .val span { color: var(--text3); font-size: 13px; margin-top: 4px; }

/* Streamlit widgets in the same style */
div.stButton > button, div.stDownloadButton > button { border-radius: 999px; padding: 0.6rem 1.5rem; font-weight: 600; border: 1px solid var(--line); background: var(--glass); color: var(--text); }
div.stButton > button[kind="primary"], div.stDownloadButton > button[kind="primary"] { background: var(--teal); color: var(--bg); border: none; box-shadow: 0 6px 28px -4px rgba(24,217,181,.45); }
div.stButton > button[kind="primary"]:hover { filter: brightness(1.08); color: var(--bg); }
div.stButton > button:disabled { opacity: .35; box-shadow: none; }
[data-testid="stFileUploaderDropzone"] { background: var(--glass); border: 1.2px dashed var(--teal-line); border-radius: 22px; padding: 28px; }
/* radio options as selectable cards (role + dataset) */
[data-testid="stRadioGroup"] { gap: 12px; flex-wrap: wrap; }
[data-testid="stRadioGroup"] > div { background: var(--glass); border: 1px solid var(--line); border-radius: 18px; padding: 16px 20px 14px; min-width: 190px; transition: border-color .15s, background .15s; }
[data-testid="stRadioGroup"] > div:hover { border-color: var(--line2); }
[data-testid="stRadioGroup"] > div[data-selected="true"] { background: var(--teal-soft); border-color: var(--teal); box-shadow: 0 0 36px rgba(24,217,181,.22); }
[data-testid="stRadioOption"] p { font-size: 16px; font-weight: 600; color: var(--text); }
[data-testid="stRadioCaption"] p { color: var(--text3); }
[data-testid="stExpander"] details { background: var(--glass); border: 1px solid var(--line); border-radius: 16px; }
[data-testid="stMultiSelect"] [data-baseweb="select"] > div { background: var(--glass); border-radius: 14px; border-color: var(--line); }
hr { border-color: var(--line); }
</style>
"""

RADAR_ICON = (f'<svg width="26" height="26" viewBox="0 0 28 28" fill="none"><circle cx="14" cy="14" r="12.5" stroke="{TEAL}" '
              f'stroke-opacity=".35"/><circle cx="14" cy="14" r="8" stroke="{TEAL}" stroke-opacity=".6"/><circle cx="14" cy="14" '
              f'r="3.5" fill="{TEAL}"/><path d="M14 14 L24 6" stroke="{TEAL}" stroke-width="1.6" stroke-linecap="round"/></svg>')
LOCK_ICON = (f'<svg width="14" height="14" viewBox="0 0 16 16" fill="none"><rect x="3" y="7" width="10" height="7" rx="2" '
             f'stroke="{TEAL}" stroke-width="1.4"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" stroke="{TEAL}" stroke-width="1.4"/></svg>')

STEPS = ["Upload", "Role", "Check", "Report"]

e = html.escape


def top_bar(active: int) -> str:
    """Logo, the 4-step indicator (active = 1..4) and the privacy promise."""
    steps = "".join(
        f'<div class="sr-step {"active" if i == active else "done" if i < active else ""}">'
        f'<span class="n">{i}</span>{name}</div>'
        for i, name in enumerate(STEPS, start=1)
    )
    return (f'<div class="sr-top"><div class="sr-logo">{RADAR_ICON}SkillRadar</div>'
            f'<div class="sr-steps">{steps}</div>'
            f'<div class="sr-pill">{LOCK_ICON}Your CV stays in memory</div></div>')


def header(eyebrow: str, title: str, sub: str = "", hero: bool = False) -> str:
    cls = "sr-h1 sr-hero" if hero else "sr-h1"
    center = " sr-center" if hero else ""
    out = f'<div class="sr-eyebrow{center}">{e(eyebrow)}</div>' if eyebrow else ""
    out += f'<div class="{cls}">{e(title)}</div>'
    if sub:
        out += f'<div class="sr-sub{center}">{e(sub)}</div>'
    return out


def radar(blips: list[tuple[str, bool]] | None = None) -> str:
    """Decorative radar for the start page; blips are (label, highlighted)."""
    blips = blips or [("Python", True), ("SQL", False), ("AWS", False), ("Tableau", False), ("R", True)]
    spots = [(-70, 30), (200, 18), (215, 170), (-80, 185), (40, 236)]
    rings = "".join(f'<div class="ring" style="inset:{i}px"></div>' for i in (0, 40, 80))
    bl = "".join(f'<div class="blip {"on" if on else ""}" style="left:{x}px;top:{y}px">{e(lbl)}</div>'
                 for (lbl, on), (x, y) in zip(blips, spots))
    return f'<div class="sr-radar">{rings}<div class="sweep"></div><div class="orb"></div>{bl}</div>'


def evidence_html(snippet: str) -> str:
    """matcher.evidence() marks the matched words as **word**. Escape everything,
    then turn the markers into a highlight."""
    safe = e(snippet or "")
    return re.sub(r"\*\*(.+?)\*\*", r"<mark>\1</mark>", safe)


def tool_row(name: str, snippet: str, kept: bool = True) -> str:
    return (f'<div class="sr-tool {"" if kept else "off"}"><div class="name">{e(name)}</div>'
            f'<div class="ev">“{evidence_html(snippet)}”</div></div>')


def stats(items: list[tuple[int, str, bool]]) -> str:
    """Small number tiles: (number, label, highlight in teal)."""
    return '<div class="sr-stats">' + "".join(
        f'<div class="sr-stat"><b class="{"teal" if hl else ""}">{int(n)}</b><span>{e(lbl)}</span></div>'
        for n, lbl, hl in items) + "</div>"


def card(title: str, body: str, strong: bool = False, extra_html: str = "") -> str:
    return (f'<div class="sr-card {"strong" if strong else ""}"><h4>{e(title)}</h4><p>{e(body)}</p>'
            f'{extra_html}</div>')


def pct(x: float) -> float:
    """Share (0..1) -> CSS percentage, clamped to 0..100."""
    return round(max(0.0, min(1.0, float(x))) * 100, 1)


def gap_row(rank: int, name: str, share: float, lo: float, hi: float, tag: str = "Missing", grey: bool = False) -> str:
    """One missing tool: bar = share of postings (100% = full track), tick = 95% interval."""
    return (f'<div class="sr-gap"><div class="rank">{rank:02d}</div><div class="tool">{e(name)}</div>'
            f'<div class="track"><div class="fill" style="width:{pct(share)}%"></div>'
            f'<div class="ci" style="left:{pct(lo)}%;width:{max(pct(hi) - pct(lo), 1.5):.1f}%"></div></div>'
            f'<div class="pct">{share:.0%}<small>{lo:.0%}–{hi:.0%}</small></div>'
            f'<div class="sr-tag {"grey" if grey else ""}">{e(tag)}</div></div>')


def chips(items: list[tuple[str, str, bool]]) -> str:
    """(name, detail, added_by_user)"""
    return '<div class="sr-chips">' + "".join(
        f'<div class="sr-chip {"added" if added else ""}">{e(n)}<span>{e(d)}</span></div>' for n, d, added in items) + "</div>"


def ring(coverage: float, label: str = "coverage") -> str:
    """Coverage ring; the arc length is coverage (0..1) of the circle."""
    r = 82
    circ = 2 * 3.14159265 * r
    dash = max(0.0, min(1.0, coverage)) * circ
    return (f'<div class="sr-ring"><svg width="190" height="190" viewBox="0 0 190 190">'
            f'<defs><linearGradient id="srg" x1="0" y1="0" x2="1" y2="1"><stop offset="0" stop-color="#7DF5DE"/>'
            f'<stop offset="1" stop-color="{TEAL}"/></linearGradient></defs>'
            f'<circle cx="95" cy="95" r="{r}" fill="none" stroke="rgba(255,255,255,.08)" stroke-width="14"/>'
            f'<circle cx="95" cy="95" r="{r}" fill="none" stroke="url(#srg)" stroke-width="14" stroke-linecap="round" '
            f'stroke-dasharray="{dash:.1f} {circ:.1f}" transform="rotate(-90 95 95)" '
            f'style="filter:drop-shadow(0 0 10px rgba(24,217,181,.35))"/></svg>'
            f'<div class="val"><b>{coverage:.0%}</b><span>{e(label)}</span></div></div>')
