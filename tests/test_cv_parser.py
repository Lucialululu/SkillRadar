"""Tests for skillradar.cv_parser."""
import pytest

from skillradar.cv_parser import clean_text, read_cv, read_cv_bytes

LONG = "Skills: Python, SQL, Docker. " * 3   # read_cv rejects texts under 50 characters


def test_clean_ligatures_and_hyphen_breaks():
    assert clean_text("sci\ufb01c Kuber-\nnetes") == "scific Kubernetes"


def test_clean_bullets_and_whitespace():
    assert clean_text("• Python\n▪   SQL\n\n\n\n- Docker") == "Python\nSQL\n\nDocker"


def test_read_txt(tmp_path):
    f = tmp_path / "cv.txt"
    f.write_text(LONG)
    assert "Docker" in read_cv(f)


def test_read_docx_including_tables(tmp_path):
    docx = pytest.importorskip("docx")
    d = docx.Document()
    d.add_paragraph("Jane Doe, MSc student at DTU, looking for a data science role.")
    t = d.add_table(rows=1, cols=2)
    t.rows[0].cells[0].text, t.rows[0].cells[1].text = "Tools", "PyTorch, Tableau"
    d.save(tmp_path / "cv.docx")
    assert "PyTorch, Tableau" in read_cv(tmp_path / "cv.docx")


def test_read_pdf(tmp_path):
    pytest.importorskip("pdfplumber")
    canvas = pytest.importorskip("reportlab.pdfgen.canvas")
    c = canvas.Canvas(str(tmp_path / "cv.pdf"))
    c.drawString(60, 800, "Jane Doe, MSc student at DTU")
    c.drawString(60, 780, "Skills: Python (pandas, scikit-learn), SQL, Docker")
    c.save()
    text = read_cv(tmp_path / "cv.pdf")
    assert "scikit-learn" in text and "Docker" in text


def test_read_cv_bytes_matches_file_and_writes_nothing(tmp_path, monkeypatch):
    docx = pytest.importorskip("docx")
    d = docx.Document()
    d.add_paragraph("Jane Doe. Skills: Python, SQL, Docker, Tableau and some more text here.")
    d.save(tmp_path / "cv.docx")
    data = (tmp_path / "cv.docx").read_bytes()
    monkeypatch.chdir(tmp_path)
    before = set(tmp_path.iterdir())
    assert read_cv_bytes(data, "upload.docx") == read_cv(tmp_path / "cv.docx")
    assert "Docker" in read_cv_bytes(LONG.encode(), "cv.txt")
    assert set(tmp_path.iterdir()) == before        # GDPR: no temp files


def test_read_cv_bytes_errors():
    with pytest.raises(ValueError, match="Unsupported"):
        read_cv_bytes(LONG.encode(), "cv.odt")


def test_errors(tmp_path):
    with pytest.raises(FileNotFoundError):
        read_cv(tmp_path / "nope.pdf")
    (tmp_path / "cv.odt").write_text(LONG)
    with pytest.raises(ValueError, match="Unsupported"):
        read_cv(tmp_path / "cv.odt")
    (tmp_path / "short.txt").write_text("Python")
    with pytest.raises(ValueError, match="scanned"):
        read_cv(tmp_path / "short.txt")
