import pytest
from PIL import Image

from biblocal.loader import LoadError, load_for_ocr
from tests.fixtures.make_bibs import make_bib_image


def test_downscales_long_side(tmp_path):
    p = make_bib_image(tmp_path / "a.jpg", "12", size=(4000, 3000))
    li = load_for_ocr(p, 2048)
    assert li.image.size == (2048, 1536)
    assert li.scale == pytest.approx(.512)
    assert li.original_size == (4000, 3000) and li.image.mode == "RGB"


@pytest.mark.parametrize("orientation", [6, 8])
def test_exif_orientation_applied(tmp_path, orientation):
    p = make_bib_image(tmp_path / "r.jpg", "12", size=(1600, 1067), exif_orientation=orientation)
    with Image.open(p) as image:
        assert image.size == (1067, 1600)
    li = load_for_ocr(p, 2048)
    assert li.image.size == (1600, 1067) and li.original_size == (1600, 1067)


def test_small_image_not_upscaled(tmp_path):
    li = load_for_ocr(make_bib_image(tmp_path / "s.jpg", "12", size=(800, 600)), 2048)
    assert (li.image.size, li.scale) == ((800, 600), 1.)


def test_corrupt_and_empty_files_raise(tmp_path):
    bad = tmp_path / "bad.jpg"
    bad.write_bytes(b"not a jpeg")
    empty = tmp_path / "empty.jpg"
    empty.write_bytes(b"")
    for path in (bad, empty):
        with pytest.raises(LoadError) as failure:
            load_for_ocr(path, 2048)
        assert failure.value.args[0] == path


def test_draft_decodes_landscape_at_reduced_resolution(tmp_path, monkeypatch):
    from PIL import JpegImagePlugin
    p = make_bib_image(tmp_path / "large.jpg", "12", size=(6000, 4000))
    original_draft = JpegImagePlugin.JpegImageFile.draft
    sizes = []

    def record_draft(image, mode, target):
        result = original_draft(image, mode, target)
        sizes.append(image.size)
        return result

    monkeypatch.setattr(JpegImagePlugin.JpegImageFile, "draft", record_draft)
    li = load_for_ocr(p, 2048)
    assert sizes[0] == (3000, 2000)
    assert li.image.size == (2048, 1365)
