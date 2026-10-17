import csv

import pytest

from scripts.spike_k1k2 import candidates, metrics, verdict, write_truth_template


def test_spike_skips_clock_distance_and_overlong_number():
    assert candidates([("BIB 247 1:23:45 10K 5km 42.195 123456", .9), ("88", .49)]) == {"247": .9}
    assert candidates([("007", .6), ("7", .95)]) == {"7": .95}


def test_spike_metrics_count_tags_not_wrong_photos():
    truth = {"a.jpg": ["007", "9"], "b.jpg": ["12"], "c.jpg": []}
    reads = {"a.jpg": {"7": .9, "13": .9}, "b.jpg": {"12": .79}, "c.jpg": {}}
    report = metrics(reads, truth, {"7", "9", "12", "13"})
    assert report == {"photos": 3, "readable": 2, "hit_rate": .5, "wrong_rate": .5}


@pytest.mark.parametrize("hit,wrong,speed,want", [
    (.70, .029, 2., ("PASS", "PASS")),
    (.70, .03, 2.01, ("WEAK", "SLOW")),
    (.50, .0, 5., ("WEAK", "SLOW")),
    (.49, .0, 5.01, ("KILL", "KILL")),
    (None, None, 1., ("n/a", "PASS")),
])
def test_spike_verdict_boundaries(hit, wrong, speed, want):
    assert verdict(hit, wrong, speed) == want


def test_truth_template_refuses_to_overwrite_labels(tmp_path):
    (tmp_path / "a.JPG").write_bytes(b"synthetic placeholder")
    write_truth_template(tmp_path)
    with (tmp_path / "truth.csv").open(newline="", encoding="utf-8") as f:
        assert list(csv.DictReader(f)) == [{"file": "a.JPG", "bibs": ""}]
    (tmp_path / "truth.csv").write_text("file,bibs\na.JPG,247\n", encoding="utf-8")
    with pytest.raises(FileExistsError):
        write_truth_template(tmp_path)
    assert "247" in (tmp_path / "truth.csv").read_text()
