import copy
import hashlib
import os
from importlib.metadata import version
from pathlib import Path

import onnxruntime
import rapidocr
from PIL import Image
from rapidocr import RapidOCR

from .models import TextHit

_MODEL_ROOT = Path(rapidocr.__file__).parent / "models"
_MODELS = (
    ("Det", "PP-OCRv6_det_small.onnx", "090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f"),
    ("Rec", "PP-OCRv6_rec_small.onnx", "6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884"),
    ("Cls", "ch_ppocr_mobile_v2.0_cls_mobile.onnx", "e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c"),
)


class OcrEngine:
    def __init__(self, max_side: int = 2048, threads: int | None = None) -> None:
        if onnxruntime.get_device() != "CPU":
            raise RuntimeError("GPU build of onnxruntime detected; install the CPU package")
        if max_side < 1:
            raise ValueError("max_side must be positive")
        if threads is not None and not 1 <= threads <= (os.cpu_count() or 1):
            raise ValueError("threads must be between 1 and the CPU count")
        onnxruntime.disable_telemetry_events()
        params = {
            "Global.max_side_len": max_side, "Global.use_cls": False,
            "Global.text_score": .5, "Global.log_level": "error",
            "Det.limit_type": "max", "Det.limit_side_len": max_side,
            "EngineConfig.onnxruntime.use_cuda": False,
            "EngineConfig.onnxruntime.use_dml": False,
            "EngineConfig.onnxruntime.use_cann": False,
            "EngineConfig.onnxruntime.use_coreml": False,
        }
        if threads is not None:
            params["EngineConfig.onnxruntime.intra_op_num_threads"] = threads
            params["EngineConfig.onnxruntime.inter_op_num_threads"] = threads
        inventory = []
        for kind, name, expected_sha in _MODELS:
            path = _MODEL_ROOT / name
            if not path.is_file():
                raise RuntimeError(f"Bundled model missing; repair the installation: {path}")
            digest = hashlib.sha256(path.read_bytes()).hexdigest()
            if digest != expected_sha:
                raise RuntimeError(f"Bundled model checksum mismatch; repair the installation: {path}")
            params[f"{kind}.model_path"] = str(path.resolve())
            inventory.append({"file": name, "bytes": path.stat().st_size, "sha256": digest})
        self._info = {"rapidocr": version("rapidocr"), "onnxruntime": version("onnxruntime"),
                      "device": "CPU", "models": inventory, "params": params}
        self._engine = RapidOCR(params=params)

    def read(self, image: Image.Image) -> list[TextHit]:
        if not isinstance(image, Image.Image):
            raise TypeError("OCR input must be a locally decoded PIL image")
        result = self._engine(image, use_det=True, use_cls=False, use_rec=True)
        if result.txts is None:
            return []
        return [TextHit(text, float(score), tuple((float(x), float(y)) for x, y in box))
                for text, score, box in zip(result.txts, result.scores, result.boxes)]

    @property
    def info(self) -> dict:
        return copy.deepcopy(self._info)
