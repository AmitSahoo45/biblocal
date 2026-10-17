from rapidocr import RapidOCR

from tests.fixtures.make_bibs import make_bib_image


def test_rapidocr_reads_synthetic_bib_on_cpu(tmp_path):
    img = make_bib_image(tmp_path / "b.jpg", "4721")
    result = RapidOCR()(str(img))
    joined = "".join(result.txts or ()).replace(" ", "")
    assert "4721" in joined
