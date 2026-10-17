import csv

from PIL import Image

from scripts.prepare_rbnr import prepare


def test_convert_text_labels_preserves_sources_and_creates_timing_copies(tmp_path):
    source = tmp_path / "rbnr" / "set1_org"
    source.mkdir(parents=True)
    for name in ["a.JPG", "b.JPG"]:
        Image.new("RGB", (32, 24), "white").save(source / name)
    before = {p.name: p.read_bytes() for p in source.glob("*.JPG")}
    (source / "list.txt").write_text(
        "Image RBN\na.JPG 007\na.JPG 247\nb.JPG 88\nTotal images 2\nTotal RBN 3\n",
        encoding="utf-8",
    )
    prepare(source.parent, tmp_path / "k1", tmp_path / "k2", sample_size=2, timing_size=1)
    with (tmp_path / "k1/truth.csv").open(newline="", encoding="utf-8") as f:
        assert list(csv.DictReader(f)) == [
            {"file": "a.JPG", "bibs": "007;247"}, {"file": "b.JPG", "bibs": "88"},
        ]
    assert {p.name: p.read_bytes() for p in source.glob("*.JPG")} == before
    assert (tmp_path / "k1/a.JPG").read_bytes() == before["a.JPG"]
    with Image.open(tmp_path / "k2/a.JPG") as image:
        assert image.size == (6000, 4000)
    assert not (tmp_path / "k2/truth.csv").exists()
