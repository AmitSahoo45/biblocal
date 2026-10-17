# Bundled OCR models

Verified again 18 Oct 2026 against the final engine's inventory and the
installed RapidOCR 3.10.0 wheel and its
`default_models.yaml` and `MODEL_LICENSES.md`. Files live under
`.venv/Lib/site-packages/rapidocr/models/`; installation supplies them.
No model is downloaded by the app. `OcrEngine.info` exposes this inventory;
the engine verifies all three checksums before use. The distribution's model
attribution notice and Apache-2.0 text are reproduced in
[THIRD_PARTY_NOTICES.md](THIRD_PARTY_NOTICES.md).

| File | Upstream/version | Bytes | SHA-256 | License |
|---|---|---:|---|---|
| PP-OCRv6_det_small.onnx | PaddleOCR PP-OCRv6 small detection; RapidOCR 3.10.0 | 9929594 | 090f04abcd9d9a7498bc4ebf677e4cb9bdce1fe4197ddb7e529f1ef44e1ff94f | Apache-2.0 |
| PP-OCRv6_rec_small.onnx | PaddleOCR PP-OCRv6 small recognition; RapidOCR 3.10.0 | 21234383 | 6f327246b50388f3c176ae304bd95767ea6dc0c9ae92153ef8cbe210b3c14884 | Apache-2.0 |
| ch_ppocr_mobile_v2.0_cls_mobile.onnx | PaddleOCR legacy v2.0 classifier; RapidOCR PP-OCRv4/mobile config, 3.10.0 | 585532 | e47acedf663230f8863ff1ab0e64dd2d82b838fceb5957146dab185a89d6215c | Apache-2.0 |

Sources recorded in the installed release manifest:

- [Detection model](https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/PP-OCRv6/det/PP-OCRv6_det_small.onnx)
- [Recognition model](https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/PP-OCRv6/rec/PP-OCRv6_rec_small.onnx)
- [Classifier model](https://www.modelscope.cn/models/RapidAI/RapidOCR/resolve/v3.10.0/onnx/PP-OCRv4/cls/ch_ppocr_mobile_v2.0_cls_mobile.onnx)
- [RapidOCR model license and attribution](https://github.com/RapidAI/RapidOCR/blob/v3.10.0/MODEL_LICENSES.md)

Upstream weights are copyright Baidu and/or the applicable PaddleOCR rights
holders. RapidOCR's conversion and packaging code is copyright RapidOCR
Authors. The package model notice identifies all three artifacts as Apache-2.0.
The classifier ships with the dependency and is checksum-verified, but is
disabled during both normal scans and benchmarks. The model files themselves
are supplied by the installed RapidOCR wheel; they are not committed here.

RapidOCR's bundled model-license notice contains older v3.9.2 source URLs
with these same hashes and names `default_models.yaml` as authoritative.
The URLs above are from the installed 3.10.0 manifest.
