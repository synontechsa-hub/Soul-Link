"""
SynCAD — Persistence Tests
Run with: python -m pytest tests/
"""
import sys, json, tempfile
from pathlib import Path
sys.path.insert(0, str(Path(__file__).parent.parent))


from core.models import Job, Sheet, Piece
from core.persistence import save_job, load_job, load_zad_file, job_to_dict, job_from_dict


def sample_job() -> Job:
    job = Job(
        name="Test Job",
        customer="Acme Workshop",
        notes="Test notes",
        material_name="Acrylic 10mm",
        blade_kerf=4,
        hourly_rate=55.0,
        markup_percent=20.0,
    )
    job.sheets = [
        Sheet(width=2440, height=1220, active=True, quantity=5,
              buy_price=95.0, sell_price=155.0, thickness=10.0, label="Full sheet"),
        Sheet(width=1200, height=600, active=False, quantity=2),
    ]
    job.pieces = [
        Piece(quantity=10, width=800, height=500, label="Side panel", can_rotate=True),
        Piece(quantity=5,  width=200, height=200, label="Corner block", can_rotate=False),
    ]
    return job


# ── Round-trip ────────────────────────────────────────────────────────────────

def test_save_and_load_roundtrip():
    job = sample_job()
    with tempfile.NamedTemporaryFile(suffix=".zcad", delete=False) as f:
        path = f.name
    save_job(job, path)
    loaded = load_job(path)

    assert loaded.name            == job.name
    assert loaded.customer        == job.customer
    assert loaded.blade_kerf      == job.blade_kerf
    assert loaded.hourly_rate     == job.hourly_rate
    assert loaded.markup_percent  == job.markup_percent
    assert len(loaded.sheets)     == len(job.sheets)
    assert len(loaded.pieces)     == len(job.pieces)


def test_sheet_fields_preserved():
    job = sample_job()
    with tempfile.NamedTemporaryFile(suffix=".zcad", delete=False) as f:
        path = f.name
    save_job(job, path)
    loaded = load_job(path)

    s0 = loaded.sheets[0]
    assert s0.width      == 2440
    assert s0.height     == 1220
    assert s0.active     is True
    assert s0.quantity   == 5
    assert s0.buy_price  == 95.0
    assert s0.sell_price == 155.0
    assert s0.thickness  == 10.0
    assert s0.label      == "Full sheet"

    s1 = loaded.sheets[1]
    assert s1.active is False


def test_piece_fields_preserved():
    job = sample_job()
    with tempfile.NamedTemporaryFile(suffix=".zcad", delete=False) as f:
        path = f.name
    save_job(job, path)
    loaded = load_job(path)

    p0 = loaded.pieces[0]
    assert p0.quantity   == 10
    assert p0.width      == 800
    assert p0.height     == 500
    assert p0.label      == "Side panel"
    assert p0.can_rotate is True

    p1 = loaded.pieces[1]
    assert p1.can_rotate is False


def test_file_is_valid_json():
    job = sample_job()
    with tempfile.NamedTemporaryFile(suffix=".zcad", delete=False) as f:
        path = f.name
    save_job(job, path)
    with open(path) as f:
        data = json.load(f)
    assert data["app"] == "SynCAD"
    assert "sheets" in data
    assert "pieces" in data


# ── ZAD import ────────────────────────────────────────────────────────────────

ZAD_CONTENT = (
    "Material: \tAcryl gegossen (gs) 10mm\r\n"
    "Mat.\t1\t1\t-1\t4100\t1200\t1\t95.64\t155.23\t10\t30\t400\r\n"
    "Mat.\t2\t0\t-1\t0\t0\t0\t0\t0\t0\t0\t0\r\n"
    "\r\n"
    "Auftrag:\t Chemie Maier Nr.:12345\r\n"
    "\r\n"
    "Sonstiges:\t 10 Lösungsbehälter\r\n"
    "Pos.\t1\t20\t800\t500\t0\r\n"
    "Pos.\t2\t5\t200\t200\t0\r\n"
    "Pos.\t3\t0\t0\t0\t0\r\n"
)


def test_import_zad():
    with tempfile.NamedTemporaryFile(suffix=".ZAD", delete=False, mode="wb") as f:
        f.write(ZAD_CONTENT.encode("latin-1"))
        path = f.name

    job = load_zad_file(path)

    assert job.material_name == "Acryl gegossen (gs) 10mm"
    assert job.customer      == "Chemie Maier Nr.:12345"
    assert job.notes         == "10 Lösungsbehälter"
    assert len(job.sheets)   == 1     # only active sheets imported
    assert job.sheets[0].width  == 4100
    assert job.sheets[0].height == 1200
    assert len(job.pieces)   == 2
    assert job.pieces[0].quantity == 20
    assert job.pieces[1].quantity == 5


def test_import_zad_kerf_and_rate():
    with tempfile.NamedTemporaryFile(suffix=".ZAD", delete=False, mode="wb") as f:
        f.write(ZAD_CONTENT.encode("latin-1"))
        path = f.name
    job = load_zad_file(path)
    assert job.blade_kerf   == 30
    assert job.hourly_rate  == 400.0


# ── Edge cases ────────────────────────────────────────────────────────────────

def test_empty_job_roundtrip():
    job = Job(name="Empty")
    with tempfile.NamedTemporaryFile(suffix=".zcad", delete=False) as f:
        path = f.name
    save_job(job, path)
    loaded = load_job(path)
    assert loaded.name == "Empty"
    assert loaded.sheets == []
    assert loaded.pieces == []


def test_job_to_dict_has_version():
    d = job_to_dict(Job(name="v"))
    assert "version" in d
    assert "saved_at" in d
