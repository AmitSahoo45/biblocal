import hashlib
import json
import subprocess
import sys
from pathlib import Path

import pytest
from PIL import Image

import biblocal.exif as exif_module
from biblocal.exif import build_args, find_exiftool, keywords_for, write_keywords
from biblocal.models import PhotoResult
from tests.fixtures.make_bibs import make_bib_image


@pytest.fixture
def exiftool():
    path = find_exiftool()
    if path is None:
        pytest.skip("exiftool is not installed")
    return path


def run_tool(exiftool, *args):
    return subprocess.run([str(exiftool), "-charset", "filename=utf8", "-@", "-"],
                          input="\n".join(map(str, args)) + "\n", capture_output=True,
                          encoding="utf-8", check=True).stdout


def metadata(exiftool, path):
    return json.loads(run_tool(exiftool, "-j", "-G1", "-s", "-XMP-dc:Subject",
                              "-IPTC:Keywords", "-XMP-lr:HierarchicalSubject", "-XMP:Rating", path))[0]


def values(info, key):
    value = info.get(key, [])
    # ExifTool JSON renders numeric-looking keyword strings as JSON numbers.
    return [str(item) for item in (value if isinstance(value, list) else [value])]


def tagged(name, bib="247", names=None):
    return PhotoResult(name, "tagged", [bib], names=names or [])


def test_keywords_defaults_template_names_and_review_abstention():
    assert keywords_for(tagged("a.jpg")) == (["247"], ["Bib|247"])
    assert keywords_for(tagged("a.jpg", names=["Jo Lee"]), with_names=True) == (["247", "Jo Lee"], ["Bib|247"])
    assert keywords_for(tagged("a.jpg"), template="Race-{bib}") == (["Race-247"], ["Bib|247"])
    assert keywords_for(PhotoResult("a.jpg", "review", ["247"], suggestions=["123"])) == ([], [])


@pytest.mark.parametrize("template", ["{unknown}", "{bib}\n-overwrite_original", "{bib}\x00"])
def test_keywords_reject_invalid_or_injected_arguments(template):
    with pytest.raises(ValueError):
        keywords_for(tagged("a.jpg"), template=template)


def test_build_args_dedupes_and_ends_with_execute(tmp_path):
    args = build_args(tmp_path / "a.jpg", ["247", "247"], ["Bib|247"], "embed", backup=True)
    assert args.index("-XMP-dc:Subject-=247") < args.index("-XMP-dc:Subject+=247")
    assert args.count("-IPTC:Keywords+=247") == 1
    assert "-overwrite_original" not in args and args[-1] == "-execute"


def test_new_sidecar_never_combines_output_with_overwrite_original(tmp_path):
    args = build_args(tmp_path / "a.jpg", ["247"], ["Bib|247"], "sidecar", backup=False)
    assert "-o" in args and "-overwrite_original" not in args
    assert str(tmp_path / "a.xmp") in args
    assert not any(arg.startswith("-IPTC:") for arg in args)


def test_new_sidecar_rejects_output_format_metacharacters(tmp_path):
    with pytest.raises(ValueError, match="percent"):
        build_args(tmp_path / "photo%c.jpg", ["247"], ["Bib|247"], "sidecar", backup=True)


def test_find_exiftool_order_and_invalid_explicit_path(tmp_path, monkeypatch):
    cli, env, on_path = [tmp_path / name for name in ("cli.exe", "env.exe", "path.exe")]
    app = tmp_path / "app"
    frozen = app / "exiftool/exiftool.exe"
    frozen.parent.mkdir(parents=True)
    for path in (cli, env, on_path, frozen):
        path.touch()
    monkeypatch.setenv("BIBLOCAL_EXIFTOOL", str(env))
    monkeypatch.setattr("biblocal.exif.shutil.which", lambda name: str(on_path))
    monkeypatch.setattr(sys, "frozen", True, raising=False)
    monkeypatch.setattr(sys, "executable", str(app / "biblocal.exe"))
    assert find_exiftool(str(cli)) == cli
    assert find_exiftool(str(tmp_path / "missing.exe")) is None
    assert find_exiftool() == env
    monkeypatch.delenv("BIBLOCAL_EXIFTOOL")
    assert find_exiftool() == frozen
    monkeypatch.setattr(sys, "frozen", False)
    assert find_exiftool() == on_path


@pytest.mark.exiftool
def test_embed_twice_no_duplicates_and_existing_keyword_preserved(tmp_path, exiftool):
    photo = make_bib_image(tmp_path / "a.jpg", "247")
    run_tool(exiftool, "-overwrite_original", "-XMP-dc:Subject=finish", photo)
    before = photo.read_bytes()
    for _ in range(2):
        report = write_keywords(tmp_path, [tagged("a.jpg")], "embed", exiftool)
        assert (report.written, report.skipped, report.failed) == (1, 0, [])
    info = metadata(exiftool, photo)
    assert sorted(values(info, "XMP-dc:Subject")) == ["247", "finish"]
    assert values(info, "IPTC:Keywords") == ["247"]
    assert values(info, "XMP-lr:HierarchicalSubject") == ["Bib|247"]
    assert Path(str(photo) + "_original").read_bytes() == before


@pytest.mark.exiftool
def test_embed_preserves_existing_latin1_iptc_text_when_writing_utf8(tmp_path, exiftool):
    photo = make_bib_image(tmp_path / "latin.jpg", "247")
    run_tool(exiftool, "-overwrite_original", "-charset", "IPTC=Latin",
             "-IPTC:Keywords=café", "-IPTC:Caption-Abstract=El niño", photo)
    report = write_keywords(tmp_path, [tagged(photo.name)], "embed", exiftool)
    assert report.written == 1 and not report.failed
    info = json.loads(run_tool(exiftool, "-j", "-G1", "-s", "-IPTC:all", photo))[0]
    assert sorted(values(info, "IPTC:Keywords")) == ["247", "café"]
    assert info["IPTC:Caption-Abstract"] == "El niño"
    assert info["IPTC:CodedCharacterSet"] == "UTF8"


@pytest.mark.exiftool
@pytest.mark.parametrize("backup", [True, False])
def test_embed_rejects_truncation_without_changing_source(tmp_path, exiftool, backup):
    photo = make_bib_image(tmp_path / "long.jpg", "247")
    old_keyword, caption, name = "é" * 40, "ñ" * 1200, "Ü" * 40
    run_tool(exiftool, "-overwrite_original", "-charset", "IPTC=Latin",
             f"-IPTC:Keywords={old_keyword}", f"-IPTC:Caption-Abstract={caption}", photo)
    before = photo.read_bytes()
    report = write_keywords(tmp_path, [tagged(photo.name, names=[name])], "embed", exiftool,
                            with_names=True, backup=backup)
    assert report.written == 0 and len(report.failed) == 1
    assert "truncated" in report.failed[0][1] and "sidecar" in report.failed[0][1]
    assert photo.read_bytes() == before
    assert not list(tmp_path.glob(".biblocal-*"))


@pytest.mark.exiftool
def test_embed_preserves_changes_made_by_another_program_during_batch(tmp_path, exiftool, monkeypatch):
    photo = make_bib_image(tmp_path / "changed.jpg", "247")
    execute = exif_module._execute_batch
    external_bytes = []

    def concurrent_edit(tool, blocks):
        outcomes = execute(tool, blocks)
        run_tool(exiftool, "-overwrite_original", "-XMP-dc:Subject=external-edit", photo)
        external_bytes.append(photo.read_bytes())
        return outcomes

    monkeypatch.setattr(exif_module, "_execute_batch", concurrent_edit)
    report = write_keywords(tmp_path, [tagged(photo.name)], "embed", exiftool)
    assert report.written == 0 and len(report.failed) == 1
    assert "changed" in report.failed[0][1]
    assert photo.read_bytes() == external_bytes[0]
    assert not Path(str(photo) + "_original").exists()


@pytest.mark.exiftool
def test_embed_backup_default_no_backup_and_pixels_unchanged(tmp_path, exiftool):
    for name, backup in (("keep.jpg", True), ("nobackup.jpg", False)):
        photo = make_bib_image(tmp_path / name, "247")
        before = photo.read_bytes()
        with Image.open(photo) as image:
            pixels = image.convert("RGB").tobytes()
        report = write_keywords(tmp_path, [tagged(name)], "embed", exiftool, backup=backup)
        assert report.written == 1 and not report.failed
        original = Path(str(photo) + "_original")
        assert original.exists() == backup
        if backup:
            assert original.read_bytes() == before
        with Image.open(photo) as image:
            assert image.convert("RGB").tobytes() == pixels


@pytest.mark.exiftool
@pytest.mark.parametrize("backup", [True, False])
def test_sidecar_create_and_preserve_source_and_existing_metadata(tmp_path, exiftool, backup):
    photos = [make_bib_image(tmp_path / name, "247") for name in ("new.jpg", "existing.jpg")]
    before = [hashlib.sha256(photo.read_bytes()).hexdigest() for photo in photos]
    sidecar = tmp_path / "existing.xmp"
    run_tool(exiftool, "-o", sidecar, "-XMP:Rating=3", "-XMP-dc:Subject=finish", photos[1])
    results = [tagged(photo.name) for photo in photos]
    for _ in range(2):
        report = write_keywords(tmp_path, results, "sidecar", exiftool, backup=backup)
        assert report.written == 2 and not report.failed
    assert [hashlib.sha256(photo.read_bytes()).hexdigest() for photo in photos] == before
    assert values(metadata(exiftool, tmp_path / "new.xmp"), "XMP-dc:Subject") == ["247"]
    existing = metadata(exiftool, sidecar)
    assert existing["XMP-xmp:Rating"] == 3
    assert sorted(values(existing, "XMP-dc:Subject")) == ["247", "finish"]


@pytest.mark.exiftool
def test_non_ascii_paths_and_names_in_same_batch(tmp_path, exiftool):
    folder = tmp_path / "Lauf 2026"
    photos = [make_bib_image(folder / name, "247") for name in ("ü 01.jpg", "ü 02.jpg")]
    results = [tagged(photo.name, names=["Jörg Peña"]) for photo in photos]
    report = write_keywords(folder, results, "embed", exiftool, with_names=True)
    assert report.written == 2 and not report.failed
    for photo in photos:
        info = metadata(exiftool, photo)
        assert values(info, "IPTC:Keywords") == ["247", "Jörg Peña"]
        assert values(info, "XMP-dc:Subject") == ["247", "Jörg Peña"]


@pytest.mark.exiftool
def test_batch_reports_failure_per_file_and_skips_unaccepted(tmp_path, exiftool):
    make_bib_image(tmp_path / "good.jpg", "247")
    make_bib_image(tmp_path / "review.jpg", "88")
    (tmp_path / "bad.jpg").write_bytes(b"not a JPEG")
    results = [tagged("bad.jpg"), tagged("good.jpg"), PhotoResult("review.jpg", "review", suggestions=["88"])]
    report = write_keywords(tmp_path, results, "embed", exiftool)
    assert (report.written, report.skipped) == (1, 1)
    assert len(report.failed) == 1 and report.failed[0][0] == "bad.jpg"
    assert "Error" in report.failed[0][1]
    assert not values(metadata(exiftool, tmp_path / "review.jpg"), "XMP-dc:Subject")


@pytest.mark.exiftool
def test_writer_rejects_escape_and_argument_injection_without_writes(tmp_path, exiftool):
    root = tmp_path / "race"
    root.mkdir()
    outside = make_bib_image(tmp_path / "outside.jpg", "247")
    before = outside.read_bytes()
    report = write_keywords(root, [tagged("../outside.jpg")], "embed", exiftool)
    assert report.written == 0 and len(report.failed) == 1
    assert outside.read_bytes() == before
    photo = make_bib_image(root / "a.jpg", "247")
    before = photo.read_bytes()
    report = write_keywords(root, [tagged("a.jpg", names=["Jo\n-overwrite_original"])], "embed", exiftool, with_names=True)
    assert report.written == 0 and len(report.failed) == 1
    assert photo.read_bytes() == before


@pytest.mark.exiftool
def test_multiple_batches_apply_template(tmp_path, exiftool):
    photos = [make_bib_image(tmp_path / f"{i}.jpg", "247") for i in range(3)]
    report = write_keywords(tmp_path, [tagged(photo.name) for photo in photos], "embed", exiftool,
                            batch_size=2, template="Race-{bib}")
    assert report.written == 3 and not report.failed
    for photo in photos:
        assert values(metadata(exiftool, photo), "XMP-dc:Subject") == ["Race-247"]
