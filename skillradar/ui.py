"""
Look and feel of the web apps (app.py, app_testing.py). Redesign, week 9.

Design idea: the app is a radar console. A framed dark "scope" with a faint plotting grid,
one family (Instrument Sans), and two colours that always mean the same thing:
    teal  (#18D9B5)  = a tool that is on your CV
    amber (#FFB13D)  = a tool that is missing
The radar itself is a real chart in the report: every top tool is a blip, and the closer
it sits to the centre, the more postings ask for it (rings = 75 / 50 / 25 % of postings).

Everything here only builds HTML/CSS strings, so app.py stays readable and these helpers
can be unit-tested (tests/test_ui.py). All strings are single-line on purpose:
st.markdown treats indented lines as code blocks.

Every piece of user or CV text goes through html.escape before it reaches the page,
so a CV containing "<script>" is shown as text, never run.
"""
from __future__ import annotations

import html
import math
import re

TEAL = "#18D9B5"
AMBER = "#FFB13D"
SWEEP_SECONDS = 6

CSS = """
<style>
@import url('https://fonts.googleapis.com/css2?family=Instrument+Sans:ital,wdth,wght@0,75..100,400..700;1,75..100,400..700&display=swap');

:root {
  --ground: #05090D; --frame: #081016; --raised: #0D161D; --raised2: #121E26;
  --ink: #E9F2F0; --ink2: #A2B4B0; --ink3: #64777A;
  --teal: #18D9B5; --teal-soft: rgba(24,217,181,.12); --teal-line: rgba(24,217,181,.42);
  --amber: #FFB13D; --amber-soft: rgba(255,177,61,.12);
  --ice: #8FE9FF;
  --line: rgba(190,225,220,.10); --line2: rgba(190,225,220,.18); --grid: rgba(190,225,220,.045);
  --ease-out: cubic-bezier(0.23, 1, 0.32, 1);
}

/* ---------- page and frame ---------- */
html, body, .stApp { font-family: 'Instrument Sans', ui-sans-serif, system-ui, -apple-system, 'Segoe UI', sans-serif; }
.stApp p, .stApp label, .stApp input, .stApp textarea, .stApp button p, .stMarkdown { font-family: inherit; }
.stApp {
  background:
    radial-gradient(60% 50% at 0% 0%, rgba(24,217,181,.16), transparent 60%),
    radial-gradient(55% 55% at 100% 100%, rgba(40,90,160,.22), transparent 60%),
    var(--ground);
  background-attachment: fixed;
}
[data-testid="stHeader"] { background: transparent; }
.block-container, [data-testid="stMainBlockContainer"] {
  position: relative; max-width: 1200px; margin: 28px auto 40px; padding: 2rem 3.6rem 3rem;
  border: 1px solid var(--line2); border-radius: 28px;
  background:
    radial-gradient(ellipse 80% 70% at 50% 35%, transparent 35%, var(--frame) 95%),
    linear-gradient(var(--grid) 1px, transparent 1px) 0 0 / 96px 96px,
    linear-gradient(90deg, var(--grid) 1px, transparent 1px) 0 0 / 96px 96px,
    var(--frame);
  box-shadow: 0 40px 120px -40px rgba(0,0,0,.8);
}
/* hatched side strips, as on a drawing frame */
.block-container::before, .block-container::after {
  content: ""; position: absolute; top: 210px; width: 34px; height: 360px; pointer-events: none;
  background: repeating-linear-gradient(135deg, rgba(190,225,220,.08) 0 1px, transparent 1px 9px);
}
.block-container::before { left: 0; border-right: 1px solid var(--line); }
.block-container::after { right: 0; border-left: 1px solid var(--line); }
@media (max-width: 760px) {
  .block-container, [data-testid="stMainBlockContainer"] { margin: 10px 8px 24px; padding: 1.2rem 1.1rem 2rem; border-radius: 20px; }
  .block-container::before, .block-container::after { display: none; }
}

/* ---------- type ---------- */
.sr-kicker { color: var(--ink3); font-size: 14px; margin: 4px 0 6px; }
.sr-h1 { color: var(--ink); font-size: 40px; font-weight: 600; font-stretch: 90%; letter-spacing: -0.025em; line-height: 1.06; margin: 0 0 12px; padding: 0; }
.sr-hero { font-size: clamp(40px, 5.4vw, 66px); letter-spacing: -0.035em; line-height: .98; margin: 18px 0 18px; max-width: 15ch; text-wrap: balance; }
.sr-grad { background: linear-gradient(95deg, var(--teal) 10%, var(--ice) 90%); -webkit-background-clip: text; background-clip: text; color: transparent; }
.sr-sub { color: var(--ink2); font-size: 18px; line-height: 1.5; margin: 0 0 24px; max-width: 46ch; }
.sr-center { text-align: center; margin-left: auto; margin-right: auto; }
.sr-muted { color: var(--ink3); font-size: 13px; }
.sr-h2 { color: var(--ink); font-size: 20px; font-weight: 600; letter-spacing: -0.01em; margin: 6px 0 4px; }
.sr-h2-sub { color: var(--ink3); font-size: 14px; margin: 0 0 14px; }
.sr-num { font-variant-numeric: tabular-nums; }

/* ---------- top bar ---------- */
.sr-top { display: flex; align-items: center; justify-content: space-between; gap: 16px; margin: 4px 0 34px; flex-wrap: wrap; }
.sr-logo { display: flex; align-items: center; gap: 12px; }
.sr-logo .word { display: flex; flex-direction: column; line-height: 1; }
.sr-logo .word b { color: var(--ink); font-weight: 700; font-size: 16px; letter-spacing: .02em; }
.sr-logo .word i { color: var(--teal); font-style: normal; font-weight: 400; font-size: 22px; letter-spacing: .01em; margin-top: 2px; }
.sr-steps { display: flex; gap: 2px; padding: 4px; border-radius: 999px; border: 1px solid var(--line2); background: rgba(5,9,13,.6); }
.sr-step { display: flex; align-items: center; gap: 8px; padding: 6px 14px 6px 7px; border-radius: 999px; color: var(--ink3); font-size: 14px; font-weight: 500; }
.sr-step .n { width: 22px; height: 22px; border-radius: 999px; display: grid; place-items: center; font-size: 12px; border: 1px solid var(--line2); color: var(--ink3); font-variant-numeric: tabular-nums; }
.sr-step.done { color: var(--ink2); }
.sr-step.done .n { border-color: var(--teal-line); color: var(--teal); }
.sr-step.active { color: var(--ink); background: var(--raised2); }
.sr-step.active .n { background: var(--teal); border-color: var(--teal); color: var(--ground); font-weight: 600; }
.sr-pill { display: inline-flex; align-items: center; gap: 9px; padding: 8px 16px; border-radius: 999px; border: 1px solid var(--line2); color: var(--ink2); font-size: 14px; font-weight: 500; background: rgba(5,9,13,.5); }
@media (max-width: 760px) { .sr-step .lbl { display: none; } .sr-step { padding: 4px; } .sr-top .sr-pill { display: none; } }

/* ---------- radar scope ---------- */
.sr-radar { position: relative; width: min(100%, 440px); aspect-ratio: 1; margin: 0 auto; }
.sr-radar svg { position: absolute; inset: 0; width: 100%; height: 100%; overflow: visible; }
.sr-radar .sweep { position: absolute; inset: 5%; border-radius: 50%;
  background: conic-gradient(from 0deg, transparent 0deg 280deg, rgba(24,217,181,.03) 290deg, rgba(24,217,181,.22) 358deg, rgba(190,255,240,.85) 359.4deg 360deg);
  animation: sr-spin %(T)ss linear infinite; }
.sr-radar .blip { position: absolute; width: 0; height: 0; }
.sr-radar .dot { position: absolute; left: -5px; top: -5px; width: 10px; height: 10px; border-radius: 50%; background: var(--c); opacity: .55;
  animation: sr-ping %(T)ss linear infinite; animation-delay: var(--d); }
.sr-radar .dot::after { content: ""; position: absolute; inset: -1px; border-radius: 50%; border: 1.5px solid var(--c); opacity: 0;
  animation: sr-halo %(T)ss var(--ease-out) infinite; animation-delay: var(--d); }
.sr-radar .lbl { position: absolute; white-space: nowrap; font-size: 12.5px; line-height: 18px; font-weight: 500; color: var(--ink2); }
.sr-radar .blip.miss .lbl { color: var(--ink); }
@keyframes sr-spin { to { transform: rotate(360deg); } }
@keyframes sr-ping { 0% { opacity: 1; box-shadow: 0 0 14px var(--c); } 45%, 100% { opacity: .55; box-shadow: none; } }
@keyframes sr-halo { 0% { opacity: .9; transform: scale(1); } 40%, 100% { opacity: 0; transform: scale(3.2); } }
@media (prefers-reduced-motion: reduce) {
  .sr-radar .sweep { animation: none; transform: rotate(40deg); }
  .sr-radar .dot, .sr-radar .dot::after { animation: none; opacity: 1; }
}
.sr-legend { display: flex; flex-wrap: wrap; gap: 6px 18px; justify-content: center; color: var(--ink3); font-size: 13px; margin: 14px 0 0; }
.sr-legend span { display: inline-flex; align-items: center; gap: 7px; }
.sr-legend i { width: 9px; height: 9px; border-radius: 50%; background: var(--c); display: inline-block; }
.sr-caption { color: var(--ink3); font-size: 13px; text-align: center; margin-top: 8px; }

/* ---------- feature cells (start page) ---------- */
.sr-cells { display: grid; grid-template-columns: repeat(3, 1fr); gap: 20px; margin: 46px 0 6px; }
.sr-cell { position: relative; padding: 22px 22px 24px; border-radius: 16px; border: 1px solid var(--line2); background: rgba(5,9,13,.72); overflow: hidden; }
.sr-cell::before { content: ""; position: absolute; left: 20%; right: 20%; top: -40px; height: 80px; background: radial-gradient(closest-side, rgba(24,217,181,.20), transparent); pointer-events: none; }
.sr-cell svg { display: block; margin-bottom: 18px; }
.sr-cell h4 { color: var(--ink); font-size: 19px; font-weight: 600; letter-spacing: -0.01em; margin: 0 0 8px; padding: 0; }
.sr-cell p { color: var(--ink2); font-size: 15px; line-height: 1.5; margin: 0; }
@media (max-width: 760px) { .sr-cells { grid-template-columns: 1fr; margin-top: 28px; } }

/* ---------- cards and stats ---------- */
.sr-card { position: relative; background: rgba(5,9,13,.72); border: 1px solid var(--line2); border-radius: 16px; padding: 20px 22px; }
.sr-card.strong { background: var(--raised); }
.sr-card h4 { color: var(--ink); font-size: 16px; font-weight: 600; margin: 0 0 8px; padding: 0; }
.sr-card p { color: var(--ink2); font-size: 14.5px; line-height: 1.55; margin: 0; }
.sr-stats { display: flex; gap: 8px; margin-top: 16px; }
.sr-stat { flex: 1; padding: 10px 14px; border-radius: 12px; background: var(--frame); }
.sr-stat b { display: block; font-size: 26px; font-weight: 600; letter-spacing: -0.02em; color: var(--ink); font-variant-numeric: tabular-nums; }
.sr-stat b.teal { color: var(--teal); }
.sr-stat b.amber { color: var(--amber); }
.sr-stat span { color: var(--ink3); font-size: 13px; }

/* ---------- step 3: found tools ---------- */
.sr-tool { padding: 3px 0 9px; }
.sr-tool .name { color: var(--ink); font-weight: 600; font-size: 16.5px; }
.sr-tool .ev { color: var(--ink3); font-size: 14px; margin-top: 2px; }
.sr-tool .ev mark { background: var(--teal-soft); color: var(--teal); font-weight: 500; padding: 0 3px; border-radius: 4px; }
.sr-tool.off .name { color: var(--ink3); text-decoration: line-through; }
.sr-tool.off .ev mark { background: none; color: var(--ink2); }

/* ---------- step 4: report ---------- */
.sr-score { display: flex; align-items: baseline; gap: 12px; margin: 8px 0 2px; }
.sr-score b { font-size: 64px; font-weight: 600; font-stretch: 85%; letter-spacing: -0.04em; color: var(--teal); line-height: 1; font-variant-numeric: tabular-nums; }
.sr-score span { color: var(--ink2); font-size: 15px; line-height: 1.4; max-width: 30ch; }
.sr-meter { display: flex; gap: 2px; height: 12px; margin: 14px 0 6px; }
.sr-meter i { display: block; height: 100%; border-radius: 2px; background: var(--amber-soft); box-shadow: inset 0 0 0 1px rgba(255,177,61,.35); }
.sr-meter i.have { background: var(--teal); box-shadow: none; }
.sr-meter-note { color: var(--ink3); font-size: 13px; line-height: 1.45; }

.sr-gap { display: grid; grid-template-columns: 22px 128px 1fr 132px auto; align-items: center; gap: 16px; padding: 12px 16px; border-radius: 12px; background: rgba(5,9,13,.6); margin-bottom: 6px; }
.sr-gap .rank { color: var(--ink3); font-size: 13px; font-variant-numeric: tabular-nums; }
.sr-gap .tool { color: var(--ink); font-weight: 600; font-size: 16px; }
.sr-gap .track { position: relative; height: 8px; border-radius: 999px; background: rgba(190,225,220,.07); }
.sr-gap .fill { position: absolute; left: 0; top: 0; bottom: 0; border-radius: 999px; background: var(--amber); }
.sr-gap.have .fill { background: var(--teal); }
.sr-gap .ci { position: absolute; top: -5px; height: 18px; border-left: 1.5px solid var(--ink); border-right: 1.5px solid var(--ink); opacity: .9; }
.sr-gap .ci::before { content: ""; position: absolute; left: 0; right: 0; top: 8px; height: 1.5px; background: var(--ink); }
.sr-gap .pct { color: var(--ink); font-size: 18px; font-weight: 600; font-variant-numeric: tabular-nums; line-height: 1.1; }
.sr-gap .pct small { display: block; color: var(--ink3); font-size: 12.5px; font-weight: 400; margin-top: 2px; }
.sr-gap .sr-tag { justify-self: end; }
.sr-tag { padding: 3px 10px; border-radius: 999px; font-size: 12.5px; font-weight: 500; background: var(--amber-soft); color: var(--amber); white-space: nowrap; }
.sr-tag.grey { background: var(--raised2); color: var(--ink2); }
@media (max-width: 760px) {
  .sr-gap { grid-template-columns: 20px 1fr auto; row-gap: 10px; }
  .sr-gap .track { grid-column: 2 / 4; grid-row: 2; }
  .sr-gap .sr-tag { grid-column: 2 / 4; justify-self: start; }
}

/* how to read the bars (explains the 95% range) */
.sr-howto { display: grid; grid-template-columns: 150px 1fr; gap: 18px; align-items: center; padding: 14px 16px; border-radius: 12px; border: 1px dashed var(--line2); margin: 0 0 14px; }
.sr-howto .demo { position: relative; height: 8px; border-radius: 999px; background: rgba(190,225,220,.07); }
.sr-howto .demo .fill { position: absolute; left: 0; top: 0; bottom: 0; width: 54%; border-radius: 999px; background: var(--amber); }
.sr-howto .demo .ci { position: absolute; left: 46%; width: 16%; top: -5px; height: 18px; border-left: 1.5px solid var(--ink); border-right: 1.5px solid var(--ink); }
.sr-howto .demo .ci::before { content: ""; position: absolute; left: 0; right: 0; top: 8px; height: 1.5px; background: var(--ink); }
.sr-howto p { color: var(--ink2); font-size: 13.5px; line-height: 1.5; margin: 0; }
.sr-howto p b { color: var(--ink); font-weight: 600; }
@media (max-width: 760px) { .sr-howto { grid-template-columns: 1fr; } }

/* chips: tools you have */
.sr-chips { display: flex; flex-wrap: wrap; gap: 8px; margin: 4px 0 8px; }
.sr-chip { display: inline-flex; align-items: center; gap: 8px; padding: 8px 14px 8px 12px; border-radius: 999px; background: var(--teal-soft); border: 1px solid transparent; color: var(--ink); font-size: 14.5px; font-weight: 600; }
.sr-chip::before { content: ""; width: 7px; height: 7px; border-radius: 50%; background: var(--teal); }
.sr-chip span { color: var(--ink2); font-weight: 400; font-size: 13.5px; font-variant-numeric: tabular-nums; }
.sr-chip.added { border-color: var(--teal-line); }
.sr-chip.added span { color: var(--teal); }

/* job overview: which jobs can you apply for? */
.sr-jobs { display: grid; gap: 10px; margin: 4px 0 10px; }
.sr-job { padding: 16px 18px; border-radius: 14px; border: 1px solid var(--line2); background: rgba(5,9,13,.6); }
.sr-job.chosen { border-color: var(--teal-line); background: var(--raised); }
.sr-job .head { display: flex; align-items: center; justify-content: space-between; gap: 12px; flex-wrap: wrap; margin-bottom: 10px; }
.sr-job .name { color: var(--ink); font-size: 18px; font-weight: 600; }
.sr-job .name small { color: var(--ink3); font-size: 13px; font-weight: 400; margin-left: 8px; }
.sr-job .bar { display: flex; height: 10px; border-radius: 999px; overflow: hidden; background: var(--amber-soft); margin: 0 0 10px; }
.sr-job .bar i { display: block; height: 100%; background: var(--teal); }
.sr-job .line { color: var(--ink2); font-size: 14.5px; line-height: 1.5; margin: 2px 0; }
.sr-job .line b.teal { color: var(--teal); font-variant-numeric: tabular-nums; }
.sr-job .line b.amber { color: var(--amber); font-variant-numeric: tabular-nums; }
.sr-tag.go { background: var(--teal-soft); color: var(--teal); }
.sr-job-detail .sr-job { margin-bottom: 14px; }
.sr-job-detail .sr-h2 { font-size: 16px; margin-top: 10px; }

/* ---------- Streamlit widgets in the same style ---------- */
div.stButton > button, div.stDownloadButton > button, div.stFormSubmitButton > button {
  border-radius: 10px; padding: 0.62rem 1.4rem; font-weight: 600; border: 1px solid var(--line2); background: rgba(5,9,13,.6); color: var(--ink);
  transition: transform 160ms var(--ease-out), background-color 160ms ease, border-color 160ms ease; }
div.stButton > button:active, div.stDownloadButton > button:active, div.stFormSubmitButton > button:active { transform: scale(0.97); }
@media (hover: hover) and (pointer: fine) { div.stButton > button:hover { border-color: var(--teal-line); color: var(--ink); } }
div.stButton > button[kind="primary"], div.stDownloadButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primary"], div.stFormSubmitButton > button[kind="primaryFormSubmit"] {
  background: var(--teal); color: var(--ground); border: none; box-shadow: 0 10px 30px -12px rgba(24,217,181,.7); }
div.stButton > button[kind="primary"]:hover, div.stDownloadButton > button[kind="primary"]:hover { filter: brightness(1.07); color: var(--ground); }
div.stButton > button:disabled { opacity: .35; box-shadow: none; }
[data-testid="stFileUploaderDropzone"] { background: rgba(5,9,13,.75); border: 1.5px dashed var(--line2); border-radius: 16px; padding: 30px 26px; transition: border-color 160ms ease; }
[data-testid="stFileUploaderDropzone"]:hover { border-color: var(--teal-line); }
[data-testid="stRadioGroup"] { gap: 12px; flex-wrap: wrap; }
[data-testid="stRadioGroup"] > div { background: rgba(5,9,13,.72); border: 1px solid var(--line2); border-radius: 16px; padding: 16px 20px 14px; min-width: 196px; transition: border-color 160ms ease, background-color 160ms ease; }
[data-testid="stRadioGroup"] > div:hover { border-color: var(--teal-line); }
[data-testid="stRadioGroup"] > div[data-selected="true"], [data-testid="stRadioGroup"] > div:has(input:checked) { background: var(--teal-soft); border-color: var(--teal); }
[data-testid="stRadioOption"] p { font-size: 16px; font-weight: 600; color: var(--ink); }
[data-testid="stRadioCaption"] p, [data-testid="stCaptionContainer"] p { color: var(--ink3); font-variant-numeric: tabular-nums; }
[data-testid="stExpander"] details { background: rgba(5,9,13,.6); border: 1px solid var(--line); border-radius: 14px; }
[data-testid="stMultiSelect"] [data-baseweb="select"] > div { background: rgba(5,9,13,.75); border-radius: 12px; border-color: var(--line2); }
[data-testid="stForm"] { border: 1px solid var(--line2); border-radius: 16px; background: rgba(5,9,13,.6); }
hr { border-color: var(--line); }
</style>
""".replace("%(T)s", str(SWEEP_SECONDS))

e = html.escape

# ---------------------------------------------------------------------------
# icons (stroke icons in the accent colour)
# ---------------------------------------------------------------------------

LOGO = (f'<svg width="34" height="34" viewBox="0 0 34 34" fill="none" aria-hidden="true">'
        f'<circle cx="17" cy="17" r="15.5" stroke="{TEAL}" stroke-opacity=".45"/>'
        f'<circle cx="17" cy="17" r="10" stroke="{TEAL}" stroke-opacity=".7"/>'
        f'<circle cx="17" cy="17" r="4.5" stroke="{TEAL}"/>'
        f'<path d="M17 17 L28.5 6.5" stroke="{TEAL}" stroke-width="1.8" stroke-linecap="round"/>'
        f'<circle cx="24" cy="23" r="2" fill="{AMBER}"/></svg>')
RADAR_ICON = LOGO                                  # kept for older imports
LOCK_ICON = (f'<svg width="14" height="14" viewBox="0 0 16 16" fill="none" aria-hidden="true"><rect x="3" y="7" width="10" height="7" rx="2" '
             f'stroke="{TEAL}" stroke-width="1.4"/><path d="M5.5 7V5a2.5 2.5 0 0 1 5 0v2" stroke="{TEAL}" stroke-width="1.4"/></svg>')
SPARK_ICON = (f'<svg width="15" height="15" viewBox="0 0 16 16" fill="none" aria-hidden="true">'
              f'<circle cx="8" cy="8" r="6.5" stroke="{TEAL}" stroke-opacity=".6"/><circle cx="8" cy="8" r="2.2" fill="{TEAL}"/></svg>')

_I = f'width="30" height="30" viewBox="0 0 30 30" fill="none" stroke="{TEAL}" stroke-width="1.6" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true"'
ICONS = {
    "scan": f'<svg {_I}><path d="M4 9V6a2 2 0 0 1 2-2h3M21 4h3a2 2 0 0 1 2 2v3M26 21v3a2 2 0 0 1-2 2h-3M9 26H6a2 2 0 0 1-2-2v-3"/><path d="M10 11h10M10 15h10M10 19h6"/></svg>',
    "check": f'<svg {_I}><rect x="4" y="4" width="22" height="22" rx="5"/><path d="m10 15.5 3.5 3.5L20.5 11"/></svg>',
    "radar": f'<svg {_I}><circle cx="15" cy="15" r="11"/><circle cx="15" cy="15" r="5.5"/><path d="M15 15 23 7"/><circle cx="20" cy="19.5" r="1.4" fill="{AMBER}" stroke="{AMBER}"/></svg>',
}

STEPS = ["Upload", "Role", "Check", "Report"]


# ---------------------------------------------------------------------------
# page parts
# ---------------------------------------------------------------------------

def top_bar(active: int, steps: list[str] | None = None) -> str:
    """Wordmark, the step indicator (active = 1..len(steps)) and the privacy promise."""
    steps = steps or STEPS
    items = "".join(
        f'<div class="sr-step {"active" if i == active else "done" if i < active else ""}">'
        f'<span class="n">{i}</span><span class="lbl">{e(name)}</span></div>'
        for i, name in enumerate(steps, start=1)
    )
    return (f'<div class="sr-top"><div class="sr-logo">{LOGO}<div class="word"><b>SKILL</b><i>RADAR</i></div></div>'
            f'<div class="sr-steps" role="list" aria-label="Progress">{items}</div>'
            f'<div class="sr-pill">{LOCK_ICON}Your CV stays in memory</div></div>')


def pill(text: str) -> str:
    return f'<div class="sr-pill">{SPARK_ICON}{e(text)}</div>'


def header(kicker: str, title: str, sub: str = "", hero: bool = False) -> str:
    """Page heading. hero=True: the large start-page headline with the teal-to-ice gradient."""
    out = f'<div class="sr-kicker">{e(kicker)}</div>' if kicker else ""
    if hero:
        out += f'<h1 class="sr-h1 sr-hero"><span class="sr-grad">{e(title)}</span></h1>'
    else:
        out += f'<h1 class="sr-h1">{e(title)}</h1>'
    if sub:
        out += f'<div class="sr-sub">{e(sub)}</div>'
    return out


def section_title(title: str, sub: str = "") -> str:
    return f'<div class="sr-h2">{e(title)}</div>' + (f'<div class="sr-h2-sub">{e(sub)}</div>' if sub else "")


def features(cells: list[tuple[str, str, str]]) -> str:
    """Three cells under the hero: (icon key, title, text)."""
    return '<div class="sr-cells">' + "".join(
        f'<div class="sr-cell">{ICONS.get(icon, "")}<h4>{e(t)}</h4><p>{e(p)}</p></div>' for icon, t, p in cells) + "</div>"


# ---------------------------------------------------------------------------
# the radar
# ---------------------------------------------------------------------------

def radar_radius(share: float) -> float:
    """Distance from the centre as a fraction of the scope radius: 100% of postings = centre,
    0% = rim. Kept a little away from both so dots never sit on the centre mark or the rim."""
    s = max(0.0, min(1.0, float(share)))
    return 0.10 + 0.82 * (1 - s)


def radar(points: list[tuple[str, float, bool]] | None = None, legend: bool = True) -> str:
    """Radar chart. points = (tool name, share of postings 0..1, on the CV).
    Bearing = rank order around the scope (most requested first, at 12 o'clock);
    distance = how often postings ask for it (rings at 75 / 50 / 25 %).
    Each blip lights up when the sweep passes its bearing."""
    if points is None:   # start page example: data scientist, primary dataset (analysis/results)
        points = [("Python", .78, True), ("SQL", .54, False), ("R", .49, True), ("AWS", .26, False),
                  ("Tableau", .22, False), ("Spark", .21, False), ("TensorFlow", .17, True)]
    pts = sorted(points, key=lambda p: -p[1])
    S, C, R = 400, 200, 180                          # svg box, centre, scope radius

    parts = [f'<svg viewBox="0 0 {S} {S}" role="img" aria-label="Radar chart of tool demand">',
             '<defs><radialGradient id="srscope"><stop offset="0" stop-color="#0E2226"/>'
             '<stop offset="1" stop-color="#05090D"/></radialGradient></defs>',
             f'<circle cx="{C}" cy="{C}" r="{R}" fill="url(#srscope)" stroke="{TEAL}" stroke-opacity=".45"/>']
    for share in (0.75, 0.5, 0.25):                  # rings mark share of postings
        r = radar_radius(share) * R
        parts.append(f'<circle cx="{C}" cy="{C}" r="{r:.1f}" fill="none" stroke="{TEAL}" stroke-opacity=".16"/>')
        parts.append(f'<text x="{C + 5}" y="{C - r - 4:.1f}" fill="#64777A" font-size="10.5" font-family="inherit">{share:.0%}</text>')
    for a in range(0, 180, 45):                      # cross hairs
        dx, dy = R * math.sin(math.radians(a)), R * math.cos(math.radians(a))
        parts.append(f'<line x1="{C - dx:.1f}" y1="{C + dy:.1f}" x2="{C + dx:.1f}" y2="{C - dy:.1f}" '
                     f'stroke="{TEAL}" stroke-opacity="{.14 if a % 90 == 0 else .07}"/>')
    for a in range(0, 360, 5):                       # bearing ticks on the rim
        long = a % 30 == 0
        r1, r2 = R, R + (9 if long else 4)
        s, c = math.sin(math.radians(a)), math.cos(math.radians(a))
        parts.append(f'<line x1="{C + r1 * s:.1f}" y1="{C - r1 * c:.1f}" x2="{C + r2 * s:.1f}" y2="{C - r2 * c:.1f}" '
                     f'stroke="{TEAL}" stroke-opacity="{.55 if long else .25}"/>')
    parts.append(f'<circle cx="{C}" cy="{C}" r="3" fill="{TEAL}"/></svg>')

    # Bearings follow the golden angle, so tools next to each other in the ranking (similar distance
    # from the centre) end up far apart around the scope instead of in one crowded wedge.
    # Labels then take the first free spot (right, left, nudged up or down); sizes in svg units.
    blips, boxes = [], []
    for i, (name, share, have) in enumerate(pts):
        bearing = (8 + i * 137.508) % 360
        r = radar_radius(share) * R
        x = C + r * math.sin(math.radians(bearing))
        y = C - r * math.cos(math.radians(bearing))
        boxes.append((x - 7, y - 7, x + 7, y + 7))                     # the dot itself
        text = f"{name} {share:.0%}"
        w, h = 6.6 * len(text) + 4, 15
        prefer_left = x > C + 25
        sides = ["l", "r"] if prefer_left else ["r", "l"]
        place = None
        for dy in (0, -13, 13, -24, 24):
            for side in sides:
                bx0 = x - 11 - w if side == "l" else x + 11
                box = (bx0, y - h / 2 + dy, bx0 + w, y + h / 2 + dy)
                if not any(box[0] < b[2] and box[2] > b[0] and box[1] < b[3] and box[3] > b[1] for b in boxes):
                    place = (side, dy, box)
                    break
            if place:
                break
        place = place or (sides[0], 0, None)
        if place[2]:
            boxes.append(place[2])
        side, dy = place[0], place[1]
        pos = (f"right:12px;top:{dy - 9:.0f}px" if side == "l" else f"left:12px;top:{dy - 9:.0f}px")
        delay = bearing / 360 * SWEEP_SECONDS
        colour = TEAL if have else AMBER
        blips.append(f'<div class="blip {"have" if have else "miss"}" style="left:{x / S * 100:.2f}%;top:{y / S * 100:.2f}%;'
                     f'--c:{colour};--d:{delay:.2f}s"><div class="dot"></div>'
                     f'<div class="lbl" style="{pos}">{e(name)} <span class="sr-num">{share:.0%}</span></div></div>')

    out = f'<div class="sr-radar">{"".join(parts)}<div class="sweep"></div>{"".join(blips)}</div>'
    if legend:
        out += (f'<div class="sr-legend"><span style="--c:{TEAL}"><i></i>On your CV</span>'
                f'<span style="--c:{AMBER}"><i></i>Missing</span><span>Closer to the centre: asked for more often</span></div>')
    return out


# ---------------------------------------------------------------------------
# step 3
# ---------------------------------------------------------------------------

def evidence_html(snippet: str) -> str:
    """matcher.evidence() marks the matched words as **word**. Escape everything,
    then turn the markers into a highlight."""
    safe = e(snippet or "")
    return re.sub(r"\*\*(.+?)\*\*", r"<mark>\1</mark>", safe)


def tool_row(name: str, snippet: str, kept: bool = True) -> str:
    return (f'<div class="sr-tool {"" if kept else "off"}"><div class="name">{e(name)}</div>'
            f'<div class="ev">“{evidence_html(snippet)}”</div></div>')


def stats(items: list[tuple[int, str, bool | str]]) -> str:
    """Small number tiles: (number, label, colour). colour: True/"teal", "amber" or False."""
    def cls(c):
        return "teal" if c is True else c if c in ("teal", "amber") else ""
    return '<div class="sr-stats">' + "".join(
        f'<div class="sr-stat"><b class="{cls(c)}">{int(n)}</b><span>{e(lbl)}</span></div>'
        for n, lbl, c in items) + "</div>"


def card(title: str, body: str, strong: bool = False, extra_html: str = "") -> str:
    return (f'<div class="sr-card {"strong" if strong else ""}"><h4>{e(title)}</h4><p>{e(body)}</p>'
            f'{extra_html}</div>')


# ---------------------------------------------------------------------------
# step 4
# ---------------------------------------------------------------------------

def pct(x: float) -> float:
    """Share (0..1) -> CSS percentage, clamped to 0..100."""
    return round(max(0.0, min(1.0, float(x))) * 100, 1)


def score(coverage: float, text: str) -> str:
    return f'<div class="sr-score"><b>{coverage:.0%}</b><span>{e(text)}</span></div>'


def coverage_meter(items: list[tuple[str, float, bool]]) -> str:
    """The coverage score drawn as its definition: one segment per top tool, width = its share
    of postings. Teal segments are on the CV, so teal length / total length = coverage."""
    total = sum(max(s, 0) for _, s, _ in items) or 1
    segs = "".join(f'<i class="{"have" if h else ""}" title="{e(n)}: {s:.0%}" style="width:{max(s, 0) / total * 100:.2f}%"></i>'
                   for n, s, h in sorted(items, key=lambda x: (not x[2], -x[1])))
    return f'<div class="sr-meter" aria-hidden="true">{segs}</div>'


def ci_howto() -> str:
    """Plain-language key for the bars, written for students who have not met confidence intervals."""
    return ('<div class="sr-howto"><div class="demo"><div class="fill"></div><div class="ci"></div></div>'
            '<p><b>Bar:</b> how many postings for this role name the tool. '
            '<b>Bracket:</b> the 95% range. We only see a sample of postings, so the true share is very likely '
            'inside this bracket. Fewer postings give a wider bracket.</p></div>')


def gap_row(rank: int, name: str, share: float, lo: float, hi: float, tag: str = "Missing",
            grey: bool = False, have: bool = False) -> str:
    """One tool: bar = share of postings (100% = full track), bracket = 95% interval."""
    tag_html = f'<div class="sr-tag {"grey" if grey else ""}">{e(tag)}</div>' if tag else "<div></div>"
    return (f'<div class="sr-gap {"have" if have else ""}"><div class="rank">{rank}</div><div class="tool">{e(name)}</div>'
            f'<div class="track"><div class="fill" style="width:{pct(share)}%"></div>'
            f'<div class="ci" style="left:{pct(lo)}%;width:{max(pct(hi) - pct(lo), 1.5):.1f}%"></div></div>'
            f'<div class="pct">{share:.0%}<small>likely {lo:.0%} to {hi:.0%}</small></div>'
            f'{tag_html}</div>')


def chips(items: list[tuple[str, str, bool]]) -> str:
    """(name, detail, added_by_user)"""
    return '<div class="sr-chips">' + "".join(
        f'<div class="sr-chip {"added" if added else ""}">{e(n)}<span>{e(d)}</span></div>' for n, d, added in items) + "</div>"


def _tool_list(names: list[str], limit: int = 6) -> str:
    if not names:
        return "none"
    shown = ", ".join(e(n) for n in names[:limit])
    return shown + (f" and {len(names) - limit} more" if len(names) > limit else "")


def job_card(name: str, n_postings: int, have_pct: float, have: list[str], missing: list[str],
             verdict: str, chosen: bool = False) -> str:
    """One job in the overview: job, % of its skills you have (and which), % you are missing (and which)."""
    tag = "go" if verdict == "You can apply" else "grey" if verdict == "Not yet" else ""
    chosen_txt = " · your chosen role" if chosen else ""
    return (f'<div class="sr-job {"chosen" if chosen else ""}"><div class="head">'
            f'<div class="name">{e(name)}<small>{n_postings:,} postings{chosen_txt}</small></div>'
            f'<div class="sr-tag {tag}">{e(verdict)}</div></div>'
            f'<div class="bar" aria-hidden="true"><i style="width:{pct(have_pct)}%"></i></div>'
            f'<div class="line">You have <b class="teal">{have_pct:.0%}</b> of the skills for this job: {_tool_list(have)}</div>'
            f'<div class="line">You are missing <b class="amber">{1 - have_pct:.0%}</b> of the skills for this job: '
            f'{_tool_list(missing)}</div></div>')


def job_cards(cards: list[str]) -> str:
    return '<div class="sr-jobs">' + "".join(cards) + "</div>"


def job_label(name: str, have_pct: float, verdict: str, chosen: bool = False) -> str:
    """Clickable expander label for one job (Streamlit markdown, not HTML)."""
    icon = {"You can apply": "🟢", "Almost there": "🟡"}.get(verdict, "⚪")
    chosen_txt = " · *your chosen role*" if chosen else ""
    clean = name.replace("[", "(").replace("]", ")")
    return (f"{icon} **{clean}** — you have :green[**{have_pct:.0%}**], "
            f"missing :orange[**{1 - have_pct:.0%}**] · {verdict}{chosen_txt}")


def job_detail(have: list[tuple[str, float]], missing: list[tuple[int, str, float, float, float]]) -> str:
    """Inside an opened job: every skill you have (chips) and every skill you miss (bars with 95% range)."""
    out = section_title(f"Skills you have ({len(have)})")
    out += (chips([(n, f"{s:.0%}", False) for n, s in have]) if have
            else '<div class="sr-muted">None of the top skills for this job yet.</div>')
    out += section_title(f"Skills you are missing ({len(missing)})", "Most requested first. The number is the skill's rank for this job.")
    out += ("".join(gap_row(r, n, s, lo, hi, tag="") for r, n, s, lo, hi in missing) if missing
            else '<div class="sr-muted">Nothing: you have all the top skills for this job.</div>')
    return f'<div class="sr-job-detail">{out}</div>'
