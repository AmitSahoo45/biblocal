import hashlib
import json
from types import SimpleNamespace

import pytest
from PIL import Image

from biblocal.cli import main
from biblocal.csv_io import read_results_csv
from biblocal.models import TextHit
from tests.fixtures.make_bibs import make_bib_folder


def test_cli_scan_outputs_and_photos_untouched(tmp_path):
    folder = make_bib_folder(tmp_path / "race", ["247"])
    before = {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()}
    assert main(["scan", str(folder)]) == 0
    out = tmp_path / "race_biblocal"
    assert read_results_csv(out / "results.csv")[0].bibs == ["247"]
    run = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert run["models"] and run["onnxruntime"] and run["device"] == "CPU"
    assert run["timing"]["median_ms"] >= 0 and run["workers"] == 1
    assert run["counts"]["tagged"] == 1
    assert (out / "review.html").exists()
    assert run["photo_root"] == str(folder.resolve())
    assert {p.name: hashlib.sha256(p.read_bytes()).hexdigest() for p in folder.iterdir()} == before


def test_cli_bad_start_list_exit_2(tmp_path, capsys):
    folder = make_bib_folder(tmp_path / "race", ["247"])
    bad = tmp_path / "bad.csv"
    bad.write_text("name\nAna\n", encoding="utf-8")
    assert main(["scan", str(folder), "--start-list", str(bad)]) == 2
    assert "bib" in capsys.readouterr().err


def test_progress_json_lines(tmp_path, capsys):
    folder = make_bib_folder(tmp_path / "race", ["247"])
    (folder / "bad.jpg").write_bytes(b"invalid JPEG")
    assert main(["scan", str(folder), "--progress", "json", "--no-review"]) == 0
    lines = [json.loads(line) for line in capsys.readouterr().out.splitlines()]
    assert [row["type"] for row in lines] == ["progress", "progress", "summary"]
    assert lines[-1]["tagged"] == 1 and lines[-1]["error"] == 1
    assert lines[-1]["skipped"] == 1
    assert not (tmp_path / "race_biblocal/review.html").exists()


def test_missing_folder_and_bad_threshold_exit_2(tmp_path, capsys):
    assert main(["scan", str(tmp_path / "missing")]) == 2
    assert "missing" in capsys.readouterr().err
    assert main(["scan", str(tmp_path), "--review", ".9", "--accept", ".5"]) == 2
    assert "review" in capsys.readouterr().err


def test_cli_rejects_output_within_photo_folder_before_ocr(tmp_path, capsys, monkeypatch):
    def unexpected_ocr(**kwargs):
        raise AssertionError("output must be validated before OCR")
    monkeypatch.setattr("biblocal.cli.OcrEngine", unexpected_ocr)
    for out in (tmp_path, tmp_path / "nested"):
        assert main(["scan", str(tmp_path), "--out", str(out)]) == 2
        assert "output" in capsys.readouterr().err.lower()


def test_cli_rejects_threshold_below_ocr_floor(tmp_path, capsys):
    assert main(["scan", str(tmp_path), "--review", ".3", "--accept", ".4"]) == 2
    assert "0.50" in capsys.readouterr().err


@pytest.mark.parametrize("height_arg,share,status", [
    (None, .02, "tagged"), ("0.04", .04, "none"), ("0", 0, "tagged"), ("1", 1, "none"),
])
def test_scan_min_bib_height_controls_filter_and_run_record(tmp_path, monkeypatch, height_arg, share, status):
    folder = tmp_path / "photos"
    folder.mkdir()
    photo = folder / "small.jpg"
    Image.new("RGB", (300, 1000), "white").save(photo)
    original = photo.read_bytes()
    hit = TextHit("247", .99, ((0, 0), (100, 0), (100, 30), (0, 30)))
    engine = SimpleNamespace(info={"device": "CPU"}, read=lambda image: [hit])
    monkeypatch.setattr("biblocal.cli.OcrEngine", lambda **kwargs: engine)
    args = ["scan", str(folder), "--no-review"]
    if height_arg is not None:
        args += ["--min-bib-height", height_arg]
    assert main(args) == 0
    out = tmp_path / "photos_biblocal"
    result = read_results_csv(out / "results.csv")[0]
    assert result.status == status
    assert result.bibs == (["247"] if status == "tagged" else [])
    run = json.loads((out / "run.json").read_text(encoding="utf-8"))
    assert run["settings"]["min_bib_height_share"] == share
    assert run["arguments"]["min_bib_height"] == share
    assert photo.read_bytes() == original


@pytest.mark.parametrize("share", ["-0.01", "1.01", "nan", "inf"])
def test_scan_rejects_invalid_min_bib_height_before_ocr(tmp_path, capsys, monkeypatch, share):
    def unexpected_ocr(**kwargs):
        raise AssertionError("height share must be checked before OCR")
    monkeypatch.setattr("biblocal.cli.OcrEngine", unexpected_ocr)
    assert main(["scan", str(tmp_path), "--min-bib-height", share]) == 2
    assert "min-bib-height" in capsys.readouterr().err
