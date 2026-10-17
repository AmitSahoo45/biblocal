import csv
import pytest

from scripts.startlist_from_truth import write_start_list
from scripts.calibrate_k1 import load_ranges, score_records
from biblocal.models import Settings


def test_start_lists_truth_and_dense(tmp_path):
    truth = tmp_path / "truth.csv"
    truth.write_text("file,bibs\na.jpg,007;9\nb.jpg,9\n", encoding="utf-8")
    out = tmp_path / "start.csv"
    write_start_list(truth, out)
    assert list(csv.DictReader(out.open())) == [{"bib": "007"}, {"bib": "9"}]
    write_start_list(truth, out, dense=True)
    assert [r["bib"] for r in csv.DictReader(out.open())] == [str(n) for n in range(1, 10)]


def test_per_set_ranges_and_weighted_wrong_rate(tmp_path):
    for name, text in (("set1", "Image RBN\nset1_01.JPG 10\nset1_02.JPG 20\nTotal 2\n"),
                       ("set2", "Image RBN\nset2_01.JPG 90\nset2_02.JPG 100\nTotal 2\n")):
        directory = tmp_path / f"{name}_org"
        directory.mkdir()
        (directory / "list.txt").write_text(text)
    ranges = load_ranges(tmp_path)
    assert ranges == {"set1": (10, 20), "set2": (90, 100)}
    box = [[0, 0], [30, 0], [30, 30], [0, 30]]
    records = [
        {"file": "set1_01.JPG", "height": 100, "hits": [{"text": "10 15 95", "score": .99, "box": box}]},
        {"file": "set2_01.JPG", "height": 100, "hits": [{"text": "95", "score": .99, "box": box}]},
    ]
    report, results = score_records(records, {"set1_01.JPG": ["10"], "set2_01.JPG": ["95"]}, ranges, "range", Settings())
    assert results[0].bibs == ["10", "15"]  # 95 belongs to another event
    assert report.hit_rate == 1 and report.wrong_rate == pytest.approx(1 / 3)
