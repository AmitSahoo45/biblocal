from pathlib import Path

import pytest
from PIL import Image

from biblocal.loader import load_for_ocr
from biblocal.ocr import OcrEngine
from tests.fixtures.make_bibs import make_bib_image


def test_reads_synthetic_number(tmp_path, engine):
    p = make_bib_image(tmp_path / "a.jpg", "4721")
    hits = engine.read(load_for_ocr(p, 2048).image)
    assert any("4721" in h.text.replace(" ", "") for h in hits)


def test_boxes_inside_image(tmp_path, engine):
    li = load_for_ocr(make_bib_image(tmp_path / "a.jpg", "88"), 2048)
    w, h = li.image.size
    hits = engine.read(li.image)
    assert hits
    assert all(0 <= x <= w and 0 <= y <= h for hit in hits for x, y in hit.box)


def test_blank_image_returns_no_hits(engine):
    assert engine.read(Image.new("RGB", (800, 600), "white")) == []


def test_refuses_gpu_build(monkeypatch):
    import onnxruntime
    monkeypatch.setattr(onnxruntime, "get_device", lambda: "GPU")
    with pytest.raises(RuntimeError, match="CPU"):
        OcrEngine()


def test_info_lists_models_with_sha256(engine):
    info = engine.info
    assert info["device"] == "CPU" and info["models"]
    assert all(len(m["sha256"]) == 64 and m["bytes"] > 0 for m in info["models"])
    text = Path("MODELS.md").read_text(encoding="utf-8")
    assert all(m["sha256"] in text for m in info["models"])


def test_params_follow_max_side():
    params = OcrEngine(max_side=3072).info["params"]
    assert params["Global.max_side_len"] == params["Det.limit_side_len"] == 3072
    assert params["Det.limit_type"] == "max"


def test_local_models_work_with_network_and_downloads_blocked(tmp_path, monkeypatch):
    import requests
    import socket
    from rapidocr.utils.download_file import DownloadFile

    def forbidden(*args, **kwargs):
        raise AssertionError("network or model download attempted")

    monkeypatch.setattr(requests.sessions.Session, "request", forbidden)
    monkeypatch.setattr(socket.socket, "connect", forbidden)
    monkeypatch.setattr(socket, "getaddrinfo", forbidden)
    monkeypatch.setattr(DownloadFile, "run", forbidden)
    local = OcrEngine(threads=1)
    p = make_bib_image(tmp_path / "offline.jpg", "4721")
    assert any("4721" in h.text for h in local.read(load_for_ocr(p, 2048).image))
    assert local._engine.text_cls is None
    for stage in (local._engine.text_det, local._engine.text_rec):
        assert stage.session.session.get_providers() == ["CPUExecutionProvider"]


def test_missing_or_corrupt_model_fails_without_downloading(tmp_path, monkeypatch):
    import biblocal.ocr as ocr
    monkeypatch.setattr(ocr, "_MODEL_ROOT", tmp_path)
    with pytest.raises(RuntimeError, match="model"):
        OcrEngine()
    (tmp_path / "PP-OCRv6_det_small.onnx").write_bytes(b"invalid synthetic model")
    with pytest.raises(RuntimeError, match="model"):
        OcrEngine()


def test_url_input_is_rejected(engine):
    with pytest.raises(TypeError, match="PIL"):
        engine.read("https://example.invalid/photo.jpg")
