import json

from PIL import Image

from biblocal.bench import bench
from biblocal.cli import main
from biblocal.models import Settings


def test_bench_respects_limit_and_reports_single_worker(tmp_path):
    for name in ("a.jpg", "b.jpg"):
        Image.new("RGB", (64, 64), "white").save(tmp_path / name)
    report = bench(tmp_path, Settings(), limit=1)
    assert report.photos == report.workers == 1
    assert report.effective_s_per_photo > 0 and report.median_ms > 0
    assert report.minutes_per_1000 == report.effective_s_per_photo * 1000 / 60


def test_eval_and_bench_cli(tmp_path, capsys):
    from biblocal.csv_io import write_results_csv
    from biblocal.models import PhotoResult
    results, truth = tmp_path / "results.csv", tmp_path / "truth.csv"
    write_results_csv([PhotoResult("a.jpg", "tagged", ["7"])], results)
    truth.write_text("file,bibs\na.jpg,7\n", encoding="utf-8")
    assert main(["eval", str(results), "--truth", str(truth)]) == 0
    assert "VERDICT K1=PASS" in capsys.readouterr().out
    photos = tmp_path / "photos"
    photos.mkdir()
    Image.new("RGB", (64, 64), "white").save(photos / "a.jpg")
    assert main(["bench", str(photos), "--limit", "1"]) == 0
    report = json.loads((tmp_path / "photos_biblocal/bench.json").read_text())
    assert report["photos"] == report["workers"] == 1
