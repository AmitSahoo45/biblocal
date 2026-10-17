import csv

import pytest
from PIL import Image, ImageOps

from tests.fixtures.make_bibs import make_bib_folder, make_bib_image


@pytest.mark.parametrize("orientation", [1, 2, 3, 4, 5, 6, 7, 8])
def test_fixture_orientation_restores_upright_pixels(tmp_path, orientation):
    ordinary = make_bib_image(tmp_path / "ordinary.jpg", "12", size=(320, 240), bib_width=100)
    rotated = make_bib_image(
        tmp_path / "rotated.jpg", "12", size=(320, 240), bib_width=100,
        exif_orientation=orientation,
    )
    with Image.open(ordinary) as a, Image.open(rotated) as b:
        assert b.getexif()[274] == orientation
        assert b.size == ((240, 320) if orientation >= 5 else (320, 240))
        upright = ImageOps.exif_transpose(b)
        assert upright.size == a.size
        # JPEG transforms can change compression error; compare visible content.
        from PIL import ImageChops, ImageStat
        assert max(ImageStat.Stat(ImageChops.difference(a, upright)).mean) < 5


def test_fixture_repeatable_and_folder_truth(tmp_path):
    a = make_bib_image(tmp_path / "a.jpg", "88", seed=12, angle=15, distractor="10K")
    b = make_bib_image(tmp_path / "b.jpg", "88", seed=12, angle=15, distractor="10K")
    assert a.read_bytes() == b.read_bytes()
    folder = make_bib_folder(tmp_path / "event", ["007", "247"])
    with (folder / "truth.csv").open(encoding="utf-8", newline="") as stream:
        assert list(csv.DictReader(stream)) == [
            {"file": "bib_0.jpg", "bibs": "007"},
            {"file": "bib_1.jpg", "bibs": "247"},
        ]
    assert len(list(folder.glob("*.jpg"))) == 2
