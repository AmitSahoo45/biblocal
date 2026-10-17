import hashlib
import json

import pytest

from biblocal.cli import main
from tests.fixtures.make_bibs import make_bib_folder
from tests.test_exif import exiftool, metadata, values


def test_missing_exiftool_returns_install_hint_before_ocr(tmp_path, capsys):
    folder = make_bib_folder(tmp_path / "race", ["247"])
    assert main(["scan", str(folder), "--write", "embed", "--exiftool", str(tmp_path / "missing.exe")]) == 2
    error = capsys.readouterr().err.lower()
    assert "exiftool" in error and "install" in error


@pytest.mark.exiftool
@pytest.mark.parametrize("mode", ["embed", "sidecar"])
def test_cli_write_explicit_modes_and_run_report(tmp_path, exiftool, mode, capsys):
    folder = make_bib_folder(tmp_path / "race", ["247"])
    photo = folder / "bib_0.jpg"
    before = hashlib.sha256(photo.read_bytes()).hexdigest()
    assert main(["scan", str(folder), "--write", mode, "--exiftool", str(exiftool),
                 "--keyword-template", "Race-{bib}", "--no-backup", "--progress", "json"]) == 0
    run = json.loads((tmp_path / "race_biblocal/run.json").read_text())
    assert run["write"] == {"mode": mode, "written": 1, "skipped": 0, "failed": []}
    summary = json.loads(capsys.readouterr().out.splitlines()[-1])
    assert summary["write"]["written"] == 1
    target = photo if mode == "embed" else photo.with_suffix(".xmp")
    assert values(metadata(exiftool, target), "XMP-dc:Subject") == ["Race-247"]
    assert not photo.with_name(photo.name + "_original").exists()
    if mode == "sidecar":
        assert hashlib.sha256(photo.read_bytes()).hexdigest() == before
