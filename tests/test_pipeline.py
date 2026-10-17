import pytest

from biblocal.csv_io import read_bib_table, read_results_csv, write_results_csv
from biblocal.models import Candidate, PhotoResult, Settings
from biblocal.pipeline import list_photos, scan_folder
from tests.fixtures.make_bibs import make_bib_folder, make_bib_image


def test_scan_synthetic_folder(tmp_path, engine):
    folder = make_bib_folder(tmp_path / "ev", ["247", "88", "1093"])
    rs = scan_folder(folder, None, Settings(), engine)
    assert [(r.file, r.status, r.bibs) for r in rs] == [
        ("bib_0.jpg", "tagged", ["247"]), ("bib_1.jpg", "tagged", ["88"]),
        ("bib_2.jpg", "tagged", ["1093"]),
    ]


def test_list_photos_filters_and_counts(tmp_path):
    for name in ["a.JPG", "b.jpeg", "c.CR3", "Thumbs.db", "sub/d.jpg", "x_biblocal/e.jpg"]:
        path = tmp_path / name
        path.parent.mkdir(parents=True, exist_ok=True)
        path.touch()
    photos, skipped = list_photos(tmp_path)
    assert [p.relative_to(tmp_path).as_posix() for p in photos] == ["a.JPG", "b.jpeg", "sub/d.jpg"]
    assert skipped == 2


def test_corrupt_file_marked_error_and_run_continues(tmp_path, engine):
    make_bib_image(tmp_path / "a.jpg", "247")
    (tmp_path / "bad.jpg").write_bytes(b"not a jpeg")
    progress = []
    rs = scan_folder(tmp_path, None, Settings(), engine,
                     lambda done, total, result: progress.append((done, total, result.file)))
    assert [r.status for r in rs] == ["tagged", "error"]
    assert rs[1].reasons == ["decode_error"]
    assert progress == [(1, 2, "a.jpg"), (2, 2, "bad.jpg")]


def test_paths_with_spaces_and_non_ascii(tmp_path, engine):
    folder = tmp_path / "Lauf 2026"
    make_bib_image(folder / "Zieleinlauf ü 01.jpg", "512")
    rs = scan_folder(folder, None, Settings(), engine)
    assert (rs[0].file, rs[0].bibs) == ("Zieleinlauf ü 01.jpg", ["512"])


def test_results_csv_round_trip(tmp_path):
    box = ((0., 0.),) * 4
    result = PhotoResult("a/ü.jpg", "tagged", ["007"], [.85], ["Ana, Silva"],
                         [Candidate("7", .85, box)], ["17"], ["mapped_chars"], 123)
    path = tmp_path / "results.csv"
    write_results_csv([result], path)
    assert read_results_csv(path) == [result]


def test_read_bib_table_preserves_zeros_empty_rows_and_rejects_duplicates(tmp_path):
    path = tmp_path / "truth.csv"
    path.write_text("\ufefffile,bibs\na.jpg,007;247\nb.jpg,\n", encoding="utf-8")
    assert read_bib_table(path) == {"a.jpg": ["007", "247"], "b.jpg": []}
    path.write_text("file,bibs\na.jpg,7\na.jpg,8\n", encoding="utf-8")
    with pytest.raises(ValueError, match="a.jpg"):
        read_bib_table(path)
