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
    assert "54%" in row and "likely 51% to 57%" in row
    assert '<div class="rank">1</div>' in row
    assert 'class="sr-gap have"' in ui.gap_row(2, "Python", .78, .75, .81, tag="", have=True)


def test_pct_is_clamped():
    assert ui.pct(1.7) == 100.0 and ui.pct(-0.2) == 0.0


def test_coverage_meter_teal_length_equals_coverage():
    items = [("Python", .78, True), ("SQL", .54, False), ("R", .49, True), ("AWS", .26, False)]
    out = ui.coverage_meter(items)
    teal = sum(float(w) for w in re.findall(r'<i class="have"[^>]*width:([\d.]+)%', out))
    assert abs(teal / 100 - (.78 + .49) / (.78 + .54 + .49 + .26)) < 0.001


def test_radar_distance_follows_demand_and_escapes_names():
    assert ui.radar_radius(1.0) < ui.radar_radius(0.5) < ui.radar_radius(0.0)
    out = ui.radar([("<b>", .5, True), ("SQL", .54, False)])
    assert ">&lt;b&gt; <span" in out
    assert out.count('class="blip') == 2 and "blip miss" in out and "blip have" in out


def test_top_bar_marks_steps():
    out = ui.top_bar(3)
    assert out.count('class="sr-step done"') == 2
    assert out.count('class="sr-step active"') == 1
    assert "Your CV stays in memory" in out
    assert ui.top_bar(4, ui.STEPS + ["Feedback"]).count('class="sr-step "') == 1


def test_stats_and_chips():
    s = ui.stats([(7, "found", False), (1, "removed", True), (2, "missing", "amber")])
    assert "<b class=\"\">7</b>" in s and "<b class=\"teal\">1</b>" in s and "<b class=\"amber\">2</b>" in s
    c = ui.chips([("Tableau", "22% · added by you", True), ("<x>", "1%", False)])
    assert 'sr-chip added' in c and "&lt;x&gt;" in c


def test_role_match_row_is_text_only_and_escapes():
    row = ui.role_match_row("Data <b>analyst", 0.64, "Strong match", ["AWS", "Kubernetes", "Spark"], chosen=True)
    assert "64%" in row and "Strong match" in row and "sr-tag go" in row and "chosen" in row
    assert "Missing most: AWS, Kubernetes" in row and "Spark" not in row      # two tools only
    assert "&lt;b&gt;" in row
    assert 'class="mark" style="left:50.0%"' in row                        # the strong-match line
    assert not any(ord(ch) > 0x2FFF for ch in row)                         # no emoji
    low = ui.role_match_row("UX designer", 0.0, "Low match", [])
    assert "sr-tag grey" in low and "No top tool missing" in low
