"""Tests for skillradar.ui: safe HTML and correct numbers (no data/ needed)."""
import re

from skillradar import ui


def test_cv_text_is_escaped_and_only_markers_become_highlights():
    out = ui.evidence_html('…<script>alert(1)</script> in **Python** & R…')
    assert "<script>" not in out and "&lt;script&gt;" in out
    assert "<mark>Python</mark>" in out and "&amp;" in out
    assert ui.evidence_html(None) == ""


def test_tool_row_escapes_name_and_marks_removed():
    assert "&lt;b&gt;" in ui.tool_row("<b>", "x")
    assert 'class="sr-tool off"' in ui.tool_row("Go", "**Go** further", kept=False)


def test_gap_row_bar_and_interval_positions():
    row = ui.gap_row(1, "SQL", 0.538, 0.506, 0.570)
    assert "width:53.8%" in row                     # bar = share of postings
    assert "left:50.6%" in row and "width:6.4%" in row   # tick from low to high
    assert "54%" in row and "51%–57%" in row
    assert ">01<" in row


def test_pct_is_clamped():
    assert ui.pct(1.7) == 100.0 and ui.pct(-0.2) == 0.0


def test_ring_arc_length_matches_coverage():
    out = ui.ring(0.47)
    dash, circ = map(float, re.search(r'stroke-dasharray="([\d.]+) ([\d.]+)"', out).groups())
    assert abs(dash / circ - 0.47) < 0.001
    assert "47%" in out


def test_top_bar_marks_steps():
    out = ui.top_bar(3)
    assert out.count('class="sr-step done"') == 2
    assert out.count('class="sr-step active"') == 1
    assert "Your CV stays in memory" in out


def test_stats_and_chips():
    s = ui.stats([(7, "found", False), (1, "removed", True)])
    assert "<b class=\"\">7</b>" in s and "<b class=\"teal\">1</b>" in s
    c = ui.chips([("Tableau", "22% · added by you", True), ("<x>", "1%", False)])
    assert 'sr-chip added' in c and "&lt;x&gt;" in c
