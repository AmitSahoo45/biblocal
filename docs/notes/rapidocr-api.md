# RapidOCR API verified for Task 1

Verified 17 Oct 2026 from the installed wheel source and actual recognition.
Python 3.13.7; RapidOCR 3.10.0; ONNX Runtime 1.31.0 (CPU); Pillow 13.0.0;
NumPy 2.5.4; opencv-python-headless 5.0.0.93; pytest 9.1.1.
No Python 3.12 fallback was needed. `.venv`, installation scratch `.tmp`, and
pip cache `D:\.cache\pip` are on D:. Base Python was already installed on C:
and is read from there; no packages were installed there.

## Call and result

Installed source paths below are relative to `.venv/Lib/site-packages/`.

```python
from rapidocr import RapidOCR
engine = RapidOCR(config_path=None, params=None)
result = engine(
    img_content, use_det=None, use_cls=None, use_rec=None,
    return_word_box=None, return_single_char_box=None,
    text_score=None, box_thresh=None, unclip_ratio=None,
)
```

Source: `rapidocr/main.py:40,93`. `params` accepts dotted keys, implemented
in `rapidocr/utils/parse_parameters.py`. Call overrides persist on the
engine (`main.py:update_params`): recognition-only fallback calls must restore
`use_det=True` before processing the next full photo.

Full OCR returns `RapidOCROutput` (`rapidocr/utils/output.py`):

| Attribute | Observed type / meaning |
|---|---|
| `boxes` | NumPy float32 `(N, 4, 2)`; coordinates in the input image |
| `txts` | tuple of strings |
| `scores` | tuple of floats |
| `elapse_list` | detection, classification, recognition seconds; disabled stage is `None` |
| `elapse` | sum of float stage times |

Blank images return an output object, with `boxes`, `txts`, `scores` all `None`,
`elapse_list=[]`, `elapse=0`, and `len(result)==0`. The spike uses
`result.txts or ()` and `result.scores or ()`. With detection off, recognition
returns `TextRecOutput` with `txts`, `scores`, `elapse`, not full OCR boxes.

Inputs accepted by `rapidocr/utils/load_image.py`: local string/Path, bytes,
PIL image, NumPy ndarray, MemoryImage and RawMemoryImage. PIL RGB is converted
internally to BGR. A three-channel ndarray is assumed already BGR.
BibLocal passes locally decoded PIL RGB images.

## Configuration and CPU

Verified keys from `rapidocr/config.yaml`:

| Key | Package default | Spike setting |
|---|---|---|
| `Global.text_score` | 0.5 | 0.5 (retain review-band candidates) |
| `Global.use_cls` | true | false |
| `Global.max_side_len` | 2000 | requested max side, 2048 in baseline |
| `Det.limit_type` | min | max |
| `Det.limit_side_len` | 736 | requested max side |
| `Det.thresh` | 0.3 | unchanged |
| `Det.box_thresh` | 0.5 | unchanged |
| `EngineConfig.onnxruntime.intra_op_num_threads` | -1 | unchanged; ORT default |
| `EngineConfig.onnxruntime.inter_op_num_threads` | -1 | unchanged; ORT default |

Both thread keys accept 1 through `os.cpu_count()`; -1 leaves the runtime
default. One worker is one sequential Python process, not one CPU thread.
Source: `rapidocr/inference_engine/onnxruntime/main.py:78`.

All four ONNX flags `use_cuda`, `use_dml`, `use_cann`, `use_coreml` are false.
`onnxruntime.get_device()` returned `CPU`, with available providers
`['AzureExecutionProvider', 'CPUExecutionProvider']`. No GPU provider was
installed or selected. Both actual detector and recognizer sessions in the
network-blocked probe reported `['CPUExecutionProvider']`.
The spike also disables ONNX telemetry before constructing its engine.

Set all three size keys together: changing only detection size does not undo
RapidOCR's preprocessing cap. Pillow uses an aspect-ratio-preserving JPEG
draft target, EXIF transpose, and thumbnail resize with no upscaling.

## Models and offline behavior

The wheel ships PP-OCRv6 small detection and recognition models (configured
language `ch`; multilingual models). The bundled legacy classifier's config
uses PP-OCRv4/mobile, but its upstream name is `ch_ppocr_mobile_v2.0_cls`.
It is disabled in the spike. Exact sizes, hashes, release source URLs and
Apache-2.0 attribution are recorded in [MODELS.md](../../MODELS.md).
All three local SHA-256 values match `rapidocr/default_models.yaml`.

Network-capable source paths found in the installed package:

- `inference_engine/onnxruntime/main.py:33-61` calls `DownloadFile.run`
  when `model_path` is unset. Existing matching files skip download, but
  missing/corrupt files trigger it. Model loading happens lazily at inference.
- `utils/download_file.py` uses Requests to retrieve missing artifacts.
- `utils/load_image.py` fetches URL image inputs using Requests.
- `ch_ppocr_rec/main.py` can obtain a dictionary when character metadata is
  absent. This bundled recognition model contains the character metadata.
- `utils/vis_res.py` can download `FZYTK.TTF` when visualization is requested.
  Do not use `result.vis()` or its font helper in BibLocal.

The spike checks bundled model existence and sets explicit absolute
`Det.model_path`, `Rec.model_path`, `Cls.model_path`, bypassing automatic
model downloads. It only accepts local photo directories and passes PIL
images. A Python audit hook blocks socket connection, DNS and datagram send
events throughout inference. Recognition succeeded with these guards.
A separate probe also replaced Requests and `DownloadFile.run` with raising
stubs and read `4721`, a blank image and a recognition-only image successfully.
These are application-level offline checks. Windows network adapters were
not disabled; an airplane-mode smoke test remains a human checkpoint check.

## Licenses

Installed metadata and wheel license files were inspected. All runtime Python
distributions declare permissive licenses except the approved tqdm and
certifi MPL-2.0 exceptions. Amit approved certifi on 17 Oct 2026, unmodified
only. Its required chain is `rapidocr -> requests -> certifi`. Its wheel
notice, source link and complete MPL-2.0 text are in
[THIRD_PARTY_NOTICES.md](../../THIRD_PARTY_NOTICES.md).
Task 11 will complete the remaining notices, including the already-approved
bundled FFmpeg and GEOS LGPL-2.1 texts. No dependency source was modified.
